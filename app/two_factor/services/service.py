# app/two_factor/services/service.py

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.core.identifiers import mask_email, normalize_email
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.infrastructure.email.base import EmailService
from app.infrastructure.email.templates import render_template
from app.infrastructure.password import hash_password, verify_password
from app.sessions.schemas import AuthenticationResponseSchema
from app.two_factor.config import settings as fa_settings
from app.two_factor.exceptions import (
    InvalidTwoFactorCodeError,
    TwoFactorAlreadyDisabledError,
    TwoFactorAlreadyEnabledError,
    TwoFactorChallengeNotFoundError,
    TwoFactorCodeExpiredError,
    TwoFactorLastMethodError,
    TwoFactorMethodAlreadyExistsError,
    TwoFactorMethodNotAvailableError,
    TwoFactorMethodNotFoundError,
    TwoFactorNotEnabledError,
    TwoFactorResendTooEarlyError,
    TwoFactorTooManyAttemptsError,
)
from app.two_factor.method_type import TwoFactorMethodType
from app.two_factor.models import TwoFactorChallenge, TwoFactorMethod
from app.two_factor.repository.repository_interface import TwoFactorRepositoryInterface
from app.two_factor.schemas import (
    TwoFactorChallengeResponseSchema,
    TwoFactorMethodSchema,
)
from app.two_factor.senders.sender_interface import TwoFactorSenderInterface
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.users.models import User

CHALLENGE_EXPIRE_MINUTES = fa_settings.CHALLENGE_EXPIRE_MINUTES
MAX_ATTEMPTS = fa_settings.MAX_ATTEMPTS
CODE_LENGTH = fa_settings.CODE_LENGTH
RESEND_COOLDOWN_SECONDS = fa_settings.RESEND_COOLDOWN_SECONDS


RECOVERY_CODE_COUNT = 10
RECOVERY_CODE_LENGTH = 10
# No look-alike characters (0/O, 1/I): the codes are written down and retyped.
RECOVERY_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _normalize_recovery_code(code: str) -> str:
    return code.replace("-", "").replace(" ", "").upper()


def _is_recovery_code(code: str) -> bool:
    return len(_normalize_recovery_code(code)) == RECOVERY_CODE_LENGTH


def _hash_recovery_code(code: str) -> str:
    # The codes are long and random, so a fast hash is enough and allows a
    # lookup by hash.
    return hashlib.sha256(_normalize_recovery_code(code).encode()).hexdigest()


class TwoFactorService(TwoFactorServiceInterface):

    def __init__(
        self,
        repository: TwoFactorRepositoryInterface,
        email_identity_repository: EmailIdentityRepositoryInterface,
        auth_session_service: AuthSessionServiceInterface,
        email_service: EmailService,
        sender: TwoFactorSenderInterface,
    ):
        self._repository = repository
        self._email_identity_repository = email_identity_repository
        self._auth_session_service = auth_session_service
        self._email_service = email_service
        self._sender = sender

    async def _get_email(self, user_id: str) -> str:
        # The confirmation address is taken from the account, not from the
        # sign-in method used. If there is none, fail closed.
        identity = await self._email_identity_repository.get_by_user_id(user_id)
        if not identity:
            raise TwoFactorMethodNotAvailableError()
        return identity.email

    async def _get_default_method(self, user_id: str) -> TwoFactorMethod | None:
        verified = [
            method
            for method in await self._repository.list_methods(user_id)
            if method.verified
        ]
        for method in verified:
            if method.is_default:
                return method
        return verified[0] if verified else None

    async def _get_notification_email(self, user_id: str) -> str | None:
        method = await self._get_default_method(user_id)
        if method is not None and method.type == TwoFactorMethodType.EMAIL:
            return method.value
        identity = await self._email_identity_repository.get_by_user_id(user_id)
        return identity.email if identity else None

    async def get_methods(self, user_id: str) -> list[TwoFactorMethodSchema]:
        return [
            TwoFactorMethodSchema(
                id=method.id,
                type=method.type,
                destination=(
                    mask_email(method.value)
                    if method.type == TwoFactorMethodType.EMAIL
                    else "***"
                ),
                is_default=method.is_default,
            )
            for method in await self._repository.list_methods(user_id)
            if method.verified
        ]

    async def _send_challenge(
        self,
        user_id: str,
        purpose: str,
        identity_id: str | None = None,
        identity_type: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        method: TwoFactorMethod | None = None,
    ) -> TwoFactorChallengeResponseSchema:
        # The code goes to the given method, otherwise to the default verified
        # method, otherwise (accounts from before methods existed) to the
        # account email.
        method = method or await self._get_default_method(user_id)
        await self._repository.invalidate_active_challenges(user_id, purpose)

        code = f"{secrets.randbelow(1_000_000):0{CODE_LENGTH}d}"
        challenge = TwoFactorChallenge(
            user_id=user_id,
            purpose=purpose,
            identity_id=identity_id,
            method_id=method.id if method else None,
            identity_type=identity_type,
            code_hash=hash_password(code),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=(
                datetime.now(timezone.utc) + timedelta(minutes=CHALLENGE_EXPIRE_MINUTES)
            ),
        )
        challenge = await self._repository.create_challenge(challenge)

        subject = "Your verification code"
        if purpose == "login":
            subject = "Confirm your login"
        elif purpose == "enable":
            subject = "Enable two-factor authentication"
        elif purpose == "disable":
            subject = "Disable two-factor authentication"
        elif purpose == "merge":
            subject = "Confirm the merge of accounts"
        elif purpose == "add_method":
            subject = "Confirm the new two-factor method"

        if method is not None:
            await self._sender.send_code(
                method=method,
                subject=subject,
                code=code,
                expires_in_minutes=CHALLENGE_EXPIRE_MINUTES,
            )
        else:
            await self._email_service.send(
                to=await self._get_email(user_id),
                subject=subject,
                body=(
                    f"Your verification code is: {code}\n\n"
                    f"The code expires in {CHALLENGE_EXPIRE_MINUTES} minutes."
                ),
            )

        return TwoFactorChallengeResponseSchema(
            challenge_id=challenge.id,
            expires_at=challenge.expires_at.isoformat(),
        )

    async def _verify_challenge(
        self,
        challenge_id: str,
        code: str,
        purpose: str,
        allow_recovery_code: bool = False,
    ) -> TwoFactorChallenge:
        challenge = await self._repository.get_challenge(challenge_id)

        if not challenge or challenge.purpose != purpose or challenge.used:
            raise TwoFactorChallengeNotFoundError()

        if challenge.expires_at <= datetime.now(timezone.utc):
            raise TwoFactorCodeExpiredError()

        if challenge.attempts >= MAX_ATTEMPTS:
            raise TwoFactorTooManyAttemptsError()

        if allow_recovery_code and _is_recovery_code(code):
            valid = await self._use_recovery_code(challenge.user_id, code)
        else:
            valid = verify_password(code, challenge.code_hash)

        if not valid:
            attempts = await self._repository.increment_challenge_attempts(challenge.id)

            if attempts >= MAX_ATTEMPTS:
                raise TwoFactorTooManyAttemptsError()

            raise InvalidTwoFactorCodeError()

        challenge.used = True
        await self._repository.update_challenge(challenge)
        return challenge

    async def _use_recovery_code(self, user_id: str, code: str) -> bool:
        recovery_code = await self._repository.get_unused_recovery_code(
            user_id,
            _hash_recovery_code(code),
        )
        if recovery_code is None:
            return False

        recovery_code.used = True
        await self._repository.update_recovery_code(recovery_code)
        return True

    async def generate_recovery_codes(self, user: User) -> list[str]:
        if not await self.is_enabled(user.id):
            raise TwoFactorNotEnabledError()

        codes = [
            "".join(
                secrets.choice(RECOVERY_CODE_ALPHABET)
                for _ in range(RECOVERY_CODE_LENGTH)
            )
            for _ in range(RECOVERY_CODE_COUNT)
        ]

        # The new set replaces the old one; only hashes are stored.
        await self._repository.replace_recovery_codes(
            user.id,
            [_hash_recovery_code(code) for code in codes],
        )

        return [f"{code[:5]}-{code[5:]}" for code in codes]

    async def is_enabled(
        self,
        user_id: str,
    ) -> bool:
        settings = await self._repository.get_settings(user_id)
        return bool(settings and settings.two_factor_enabled)

    async def authenticate_or_challenge(
        self,
        user: User,
        identity_id: str,
        identity_type: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema:
        # 2FA belongs to the account: it applies to every sign-in method.
        if not await self.is_enabled(user.id):
            tokens = await self._auth_session_service.create_tokens(
                user_id=user.id,
                identity_id=identity_id,
                identity_type=identity_type,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            return AuthenticationResponseSchema(
                **tokens.model_dump(),
                requires_two_factor=False,
            )

        challenge = await self._send_challenge(
            user_id=user.id,
            purpose="login",
            identity_id=identity_id,
            identity_type=identity_type,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return AuthenticationResponseSchema(
            requires_two_factor=True,
            challenge_id=challenge.challenge_id,
            access_token=None,
            refresh_token=None,
            token_type="bearer",
        )

    async def confirm_login(
        self,
        challenge_id: str,
        code: str,
        allow_recovery_code=True,
    ) -> AuthenticationResponseSchema:
        challenge = await self._verify_challenge(
            challenge_id,
            code,
            "login",
        )

        if challenge.identity_id is None or challenge.identity_type is None:
            raise TwoFactorChallengeNotFoundError()

        tokens = await self._auth_session_service.create_tokens(
            user_id=challenge.user_id,
            identity_id=challenge.identity_id,
            identity_type=challenge.identity_type,
            ip_address=challenge.ip_address,
            user_agent=challenge.user_agent,
        )

        return AuthenticationResponseSchema(
            **tokens.model_dump(),
            requires_two_factor=False,
        )

    async def resend_login_code(
        self,
        challenge_id: str,
    ) -> TwoFactorChallengeResponseSchema:
        challenge = await self._repository.get_challenge(challenge_id)

        if (
            not challenge
            or challenge.purpose != "login"
            or challenge.used
            or challenge.identity_id is None
            or challenge.identity_type is None
        ):
            raise TwoFactorChallengeNotFoundError()

        if challenge.attempts >= MAX_ATTEMPTS:
            raise TwoFactorTooManyAttemptsError()

        elapsed = (datetime.now(timezone.utc) - challenge.created_at).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            retry_after = int(RESEND_COOLDOWN_SECONDS - elapsed) + 1
            raise TwoFactorResendTooEarlyError(
                f"Verification code was sent recently, try again in {retry_after} seconds"
            )

        # The previous code is invalidated: only the new one works.
        return await self._send_challenge(
            user_id=challenge.user_id,
            purpose="login",
            identity_id=challenge.identity_id,
            identity_type=challenge.identity_type,
            ip_address=challenge.ip_address,
            user_agent=challenge.user_agent,
        )

    async def request_enable(self, user: User) -> TwoFactorChallengeResponseSchema:
        settings = await self._repository.get_or_create_settings(
            user.id,
        )

        if settings.two_factor_enabled:
            raise TwoFactorAlreadyEnabledError()

        # Enabling requires at least one verified method.
        if await self._get_default_method(user.id) is None:
            raise TwoFactorMethodNotAvailableError()

        return await self._send_challenge(
            user_id=user.id,
            purpose="enable",
        )

    async def confirm_enable(
        self,
        user: User,
        challenge_id: str,
        code: str,
    ) -> None:
        challenge = await self._verify_challenge(
            challenge_id,
            code,
            "enable",
        )

        if challenge.user_id != user.id:
            raise TwoFactorChallengeNotFoundError()

        settings = await self._repository.get_or_create_settings(user.id)
        if settings.two_factor_enabled:
            raise TwoFactorAlreadyEnabledError()

        settings.two_factor_enabled = True
        await self._repository.update_settings(settings)

        await self._send_action_notification(
            await self._get_notification_email(user.id),
            "enable",
        )

    async def request_disable(
        self,
        user: User,
    ) -> TwoFactorChallengeResponseSchema:
        settings = await self._repository.get_or_create_settings(
            user.id,
        )

        if not settings.two_factor_enabled:
            raise TwoFactorAlreadyDisabledError()

        return await self._send_challenge(
            user_id=user.id,
            purpose="disable",
        )

    async def confirm_disable(
        self,
        user: User,
        challenge_id: str,
        code: str,
    ) -> None:
        challenge = await self._verify_challenge(
            challenge_id,
            code,
            "disable",
        )

        if challenge.user_id != user.id:
            raise TwoFactorChallengeNotFoundError()

        settings = await self._repository.get_or_create_settings(user.id)
        if not settings.two_factor_enabled:
            raise TwoFactorAlreadyDisabledError()

        settings.two_factor_enabled = False
        await self._repository.update_settings(settings)

        # Old recovery codes must not come back when 2FA is enabled again.
        await self._repository.delete_recovery_codes(user.id)

        await self._send_action_notification(
            await self._get_notification_email(user.id),
            "disable",
        )

    async def _send_action_notification(
        self,
        email: str | None,
        action: str,
    ) -> None:
        if email is None:
            return
        template_name = {
            "enable": "TWO_FACTOR_ENABLED",
            "disable": "TWO_FACTOR_DISABLED",
        }[action]
        subject, body = render_template(template_name)
        await self._email_service.send(
            to=email,
            subject=subject,
            body=body,
        )

    async def request_add_email_method(
        self,
        user: User,
        email: str,
    ) -> TwoFactorChallengeResponseSchema:
        value = normalize_email(email)

        method: TwoFactorMethod | None = None
        for existing in await self._repository.list_methods(user.id):
            if existing.type == TwoFactorMethodType.EMAIL and existing.value == value:
                if existing.verified:
                    raise TwoFactorMethodAlreadyExistsError()
                # An unconfirmed method is reused: a new code is sent to it.
                method = existing
                break

        if method is None:
            method = await self._repository.create_method(
                TwoFactorMethod(
                    user_id=user.id,
                    type=TwoFactorMethodType.EMAIL,
                    value=value,
                )
            )

        return await self._send_challenge(
            user_id=user.id,
            purpose="add_method",
            method=method,
        )

    async def confirm_add_email_method(
        self,
        user: User,
        challenge_id: str,
        code: str,
    ) -> None:
        challenge = await self._verify_challenge(
            challenge_id,
            code,
            "add_method",
        )

        if challenge.user_id != user.id or challenge.method_id is None:
            raise TwoFactorChallengeNotFoundError()

        method = await self._repository.get_method(user.id, challenge.method_id)
        if method is None:
            raise TwoFactorChallengeNotFoundError()

        # The first verified method becomes the default one.
        methods = await self._repository.list_methods(user.id)
        has_default = any(
            m.id != method.id and m.verified and m.is_default for m in methods
        )

        method.verified = True
        method.is_default = not has_default
        await self._repository.update_method(method)

    async def remove_method(
        self,
        user: User,
        method_id: str,
    ) -> None:
        method = await self._repository.get_method(user.id, method_id)
        if method is None:
            raise TwoFactorMethodNotFoundError()

        others = [
            m
            for m in await self._repository.list_methods(user.id)
            if m.id != method.id and m.verified
        ]

        if method.verified:
            settings = await self._repository.get_or_create_settings(user.id)
            if settings.two_factor_enabled and not others:
                raise TwoFactorLastMethodError()

        was_default = method.is_default

        # Challenges refer to the method, so they are removed with it.
        await self._repository.delete_challenges_by_method_id(method.id)
        await self._repository.delete_method(method)

        # If the default method is removed, another verified one takes its place.
        if was_default and others:
            others[0].is_default = True
            await self._repository.update_method(others[0])

    async def request_merge_challenge(
        self,
        user: User,
    ) -> TwoFactorChallengeResponseSchema:
        return await self._send_challenge(
            user_id=user.id,
            purpose="merge",
        )

    async def confirm_merge_challenge(
        self,
        user_id: str,
        challenge_id: str,
        code: str,
    ) -> None:
        challenge = await self._verify_challenge(
            challenge_id,
            code,
            "merge",
        )

        if challenge.user_id != user_id:
            raise TwoFactorChallengeNotFoundError()
