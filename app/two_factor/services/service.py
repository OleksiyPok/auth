# app/two_factor/services/service.py

import secrets
from datetime import datetime, timedelta, timezone

from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.infrastructure.email.base import EmailService
from app.infrastructure.email.templates import TEMPLATE_REGISTRY
from app.infrastructure.password import hash_password, verify_password
from app.sessions.schemas import AuthenticationResponseSchema
from app.two_factor.config import settings as fa_settings
from app.two_factor.exceptions import (
    InvalidTwoFactorCodeError,
    TwoFactorAlreadyDisabledError,
    TwoFactorAlreadyEnabledError,
    TwoFactorChallengeNotFoundError,
    TwoFactorCodeExpiredError,
    TwoFactorTooManyAttemptsError,
)
from app.two_factor.models import TwoFactorChallenge
from app.two_factor.repository.repository_interface import TwoFactorRepositoryInterface
from app.two_factor.schemas import TwoFactorChallengeResponseSchema
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.users.models import User

CHALLENGE_EXPIRE_MINUTES = fa_settings.CHALLENGE_EXPIRE_MINUTES
MAX_ATTEMPTS = fa_settings.MAX_ATTEMPTS
CODE_LENGTH = fa_settings.CODE_LENGTH


class TwoFactorService(TwoFactorServiceInterface):

    def __init__(
        self,
        repository: TwoFactorRepositoryInterface,
        auth_session_service: AuthSessionServiceInterface,
        email_service: EmailService,
    ):
        self._repository = repository
        self._auth_session_service = auth_session_service
        self._email_service = email_service

    async def _send_challenge(
        self,
        user: User,
        email: str,
        identity_id: str,
        purpose: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TwoFactorChallengeResponseSchema:
        await self._repository.invalidate_active_challenges(
            user.id, purpose, identity_id
        )

        code = f"{secrets.randbelow(1_000_000):0{CODE_LENGTH}d}"
        challenge = TwoFactorChallenge(
            user_id=user.id,
            purpose=purpose,
            identity_id=identity_id,
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
            subject = "Confirm your email login"
        elif purpose == "enable":
            subject = "Enable email two-factor authentication"
        elif purpose == "disable":
            subject = "Disable email two-factor authentication"

        await self._email_service.send(
            to=email,
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
        email: str,
        two_factor_enabled: bool,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema:
        if not two_factor_enabled:
            tokens = await self._auth_session_service.create_tokens(
                user_id=user.id,
                identity_id=identity_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            return AuthenticationResponseSchema(
                **tokens.model_dump(),
                requires_two_factor=False,
            )

        challenge = await self._send_challenge(
            user=user,
            email=email,
            identity_id=identity_id,
            purpose="login",
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

        tokens = await self._auth_session_service.create_tokens(
            user_id=challenge.user_id,
            identity_id=challenge.identity_id,
            ip_address=challenge.ip_address,
            user_agent=challenge.user_agent,
        )

        return AuthenticationResponseSchema(
            **tokens.model_dump(),
            requires_two_factor=False,
        )

    async def request_enable(
        self,
        user: User,
        identity_id: str,
        email: str,
    ) -> TwoFactorChallengeResponseSchema:
        settings = await self._repository.get_or_create_settings(
            user.id,
        )

        if settings.two_factor_enabled:
            raise TwoFactorAlreadyEnabledError()

        return await self._send_challenge(
            user=user,
            email=email,
            identity_id=identity_id,
            purpose="enable",
        )

    async def confirm_enable(
        self,
        user: User,
        email: str,
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
            email,
            "enable",
        )

    async def request_disable(
        self,
        user: User,
        identity_id: str,
        email: str,
    ) -> TwoFactorChallengeResponseSchema:
        settings = await self._repository.get_or_create_settings(
            user.id,
        )

        if not settings.two_factor_enabled:
            raise TwoFactorAlreadyDisabledError()

        return await self._send_challenge(
            user=user,
            email=email,
            identity_id=identity_id,
            purpose="disable",
        )

    async def confirm_disable(
        self,
        user: User,
        email: str,
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
            email,
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
        template = TEMPLATE_REGISTRY[template_name]
        rendered = template.substitute()
        subject, body = rendered.split("\n\n", 1)
        subject = subject.removeprefix("Subject: ")
        await self._email_service.send(
            to=email,
            subject=subject,
            body=body,
        )
