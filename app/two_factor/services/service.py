# app/two_factor/services/service.py

import secrets
from datetime import datetime, timedelta, timezone

from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.infrastructure.email.base import EmailService
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

CHALLENGE_EXPIRE_MINUTES = fa_settings.CHALLENGE_EXPIRE_MINUTES = 15
MAX_ATTEMPTS = fa_settings.MAX_ATTEMPTS = 5
CODE_LENGTH = fa_settings.CODE_LENGTH = 6


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
        purpose: str,
        provider: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TwoFactorChallengeResponseSchema:
        await self._repository.invalidate_active_challenges(
            user.id,
            purpose,
            provider,
        )

        code = f"{secrets.randbelow(1_000_000):0{CODE_LENGTH}d}"
        challenge = TwoFactorChallenge(
            user_id=user.id,
            purpose=purpose,
            code_hash=hash_password(code),
            provider=provider,
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
            to=user.email,
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
        provider: str,
    ) -> TwoFactorChallenge:
        challenge = await self._repository.get_challenge(challenge_id)

        if (
            not challenge
            or challenge.purpose != purpose
            or challenge.provider != provider
            or challenge.used
        ):
            raise TwoFactorChallengeNotFoundError()

        if challenge.expires_at <= datetime.now(timezone.utc):
            raise TwoFactorCodeExpiredError()

        if challenge.attempts >= MAX_ATTEMPTS:
            raise TwoFactorTooManyAttemptsError()

        if not verify_password(code, challenge.code_hash):
            challenge.attempts += 1
            await self._repository.update_challenge(challenge)

            if challenge.attempts >= MAX_ATTEMPTS:
                raise TwoFactorTooManyAttemptsError()

            raise InvalidTwoFactorCodeError()

        challenge.used = True
        await self._repository.update_challenge(challenge)
        return challenge

    async def is_enabled(
        self,
        user_id: str,
        provider: str,
    ) -> bool:
        settings = await self._repository.get_settings(user_id, provider)
        return bool(settings and settings.two_factor_enabled)

    async def authenticate_or_challenge(
        self,
        user: User,
        provider: str,
        two_factor_enabled: bool,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema:
        if not two_factor_enabled:
            tokens = await self._auth_session_service.create_tokens(
                user_id=user.id,
                provider=provider,
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
            provider=provider,
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
        provider: str,
    ) -> AuthenticationResponseSchema:
        challenge = await self._verify_challenge(
            challenge_id,
            code,
            "login",
            provider,
        )

        tokens = await self._auth_session_service.create_tokens(
            user_id=challenge.user_id,
            provider=provider,
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
        provider: str,
    ) -> TwoFactorChallengeResponseSchema:
        settings = await self._repository.get_or_create_settings(user.id, provider)

        if settings.two_factor_enabled:
            raise TwoFactorAlreadyEnabledError()

        return await self._send_challenge(user, "enable", provider)

    async def confirm_enable(
        self,
        user: User,
        challenge_id: str,
        code: str,
        provider: str,
    ) -> None:
        challenge = await self._verify_challenge(
            challenge_id,
            code,
            "enable",
            provider,
        )

        if challenge.user_id != user.id:
            raise TwoFactorChallengeNotFoundError()

        settings = await self._repository.get_or_create_settings(user.id, provider)
        if settings.two_factor_enabled:
            raise TwoFactorAlreadyEnabledError()

        settings.two_factor_enabled = True
        await self._repository.update_settings(settings)

    async def request_disable(
        self,
        user: User,
        provider: str,
    ) -> TwoFactorChallengeResponseSchema:
        settings = await self._repository.get_or_create_settings(user.id, provider)

        if not settings.two_factor_enabled:
            raise TwoFactorAlreadyDisabledError()

        return await self._send_challenge(user, "disable", provider)

    async def confirm_disable(
        self,
        user: User,
        challenge_id: str,
        code: str,
        provider: str,
    ) -> None:
        challenge = await self._verify_challenge(
            challenge_id,
            code,
            "disable",
            provider,
        )

        if challenge.user_id != user.id:
            raise TwoFactorChallengeNotFoundError()

        settings = await self._repository.get_or_create_settings(user.id, provider)
        if not settings.two_factor_enabled:
            raise TwoFactorAlreadyDisabledError()

        settings.two_factor_enabled = False
        await self._repository.update_settings(settings)
