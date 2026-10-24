# app/two_factor/services/service.py

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
    TwoFactorMethodAlreadyExistsError,
    TwoFactorMethodNotAvailableError,
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

    async def get_methods(self, user_id: str) -> list[TwoFactorMethodSchema]:
        identity = await self._email_identity_repository.get_by_user_id(user_id)
        if not identity:
            return []
        return [
            TwoFactorMethodSchema(
                type="email",
                destination=mask_email(identity.email),
            )
        ]

    async def _send_challenge(
        self,
        user: User,
        purpose: str,
        identity_id: str | None = None,
        identity_type: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        method: TwoFactorMethod | None = None,
    ) -> TwoFactorChallengeResponseSchema:
        await self._repository.invalidate_active_challenges(user.id, purpose)

        code = f"{secrets.randbelow(1_000_000):0{CODE_LENGTH}d}"
        challenge = TwoFactorChallenge(
            user_id=user.id,
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
            # Without a method the code goes to the account email.
            await self._email_service.send(
                to=await self._get_email(user.id),
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
    ) -> TwoFactorChallenge:
        challenge = await self._repository.get_challenge(challenge_id)

        if not challenge or challenge.purpose != purpose or challenge.used:
            raise TwoFactorChallengeNotFoundError()

        if challenge.expires_at <= datetime.now(timezone.utc):
            raise TwoFactorCodeExpiredError()

        if challenge.attempts >= MAX_ATTEMPTS:
            raise TwoFactorTooManyAttemptsError()

        if not verify_password(code, challenge.code_hash):
            attempts = await self._repository.increment_challenge_attempts(challenge.id)

            if attempts >= MAX_ATTEMPTS:
                raise TwoFactorTooManyAttemptsError()

            raise InvalidTwoFactorCodeError()

        challenge.used = True
        await self._repository.update_challenge(challenge)
        return challenge

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
            user=user,
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

    async def request_enable(self, user: User) -> TwoFactorChallengeResponseSchema:
        settings = await self._repository.get_or_create_settings(
            user.id,
        )

        if settings.two_factor_enabled:
            raise TwoFactorAlreadyEnabledError()

        return await self._send_challenge(
            user=user,
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
            await self._get_email(user.id),
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
            user=user,
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

        await self._send_action_notification(
            await self._get_email(user.id),
            "disable",
        )

    async def _send_action_notification(
        self,
        email: str,
        action: str,
    ) -> None:
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
            user=user,
            purpose="add_method",
            method=method,
        )

    async def request_merge_challenge(
        self,
        user: User,
    ) -> TwoFactorChallengeResponseSchema:
        return await self._send_challenge(
            user=user,
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
