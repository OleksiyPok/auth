# app/email_auth/services/link_service.py

import secrets
from datetime import datetime, timedelta, timezone

from app.core.identifiers import normalize_email
from app.email_auth.exceptions import (
    EmailLinkRequestNotFoundError,
    EmailVerificationCodeExpiredError,
    EmailVerificationTooManyAttemptsError,
    InvalidEmailVerificationCodeError,
)
from app.email_auth.models import EmailIdentity, EmailLinkRequest
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.email_auth.schemas import (
    EmailLinkChallengeResponseSchema,
    EmailLinkConfirmRequestSchema,
    EmailLinkRequestSchema,
)
from app.email_auth.services.link_service_interface import EmailLinkServiceInterface
from app.identities.exceptions import IdentityConflictError, IdentityTypeConflictError
from app.infrastructure.email.base import EmailService
from app.infrastructure.password import hash_password, verify_password
from app.two_factor.config import settings as fa_settings

CHALLENGE_EXPIRE_MINUTES = fa_settings.CHALLENGE_EXPIRE_MINUTES
MAX_ATTEMPTS = fa_settings.MAX_ATTEMPTS
CODE_LENGTH = fa_settings.CODE_LENGTH


class EmailLinkService(EmailLinkServiceInterface):
    """Adding an email identity to an existing user."""

    def __init__(
        self,
        email_identity_repository: EmailIdentityRepositoryInterface,
        email_service: EmailService,
    ):
        self._email_identity_repository = email_identity_repository
        self._email_service = email_service

    async def request_link(
        self,
        user_id: str,
        data: EmailLinkRequestSchema,
    ) -> EmailLinkChallengeResponseSchema:
        email = normalize_email(data.email)

        if await self._email_identity_repository.get_by_user_id(user_id):
            raise IdentityTypeConflictError()

        if await self._email_identity_repository.get_by_email(email):
            raise IdentityConflictError()

        # A pending request does not reserve the address: a new request of
        # the same user replaces the previous one.
        await self._email_identity_repository.delete_link_requests_by_user_id(user_id)

        code = f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"
        link_request = await self._email_identity_repository.create_link_request(
            EmailLinkRequest(
                user_id=user_id,
                email=email,
                password_hash=hash_password(data.password),
                code_hash=hash_password(code),
                expires_at=(
                    datetime.now(timezone.utc)
                    + timedelta(minutes=CHALLENGE_EXPIRE_MINUTES)
                ),
            )
        )

        await self._email_service.send(
            to=email,
            subject="Confirm your email address",
            body=(
                f"Your verification code is: {code}\n\n"
                f"The code expires in {CHALLENGE_EXPIRE_MINUTES} minutes."
            ),
        )

        return EmailLinkChallengeResponseSchema(
            challenge_id=link_request.id,
            expires_at=link_request.expires_at.isoformat(),
        )

    async def confirm_link(
        self,
        user_id: str,
        data: EmailLinkConfirmRequestSchema,
    ) -> EmailIdentity:
        link_request = await self._email_identity_repository.get_link_request(
            data.challenge_id
        )

        # A request of another user is reported as not found.
        if link_request is None or link_request.user_id != user_id:
            raise EmailLinkRequestNotFoundError()

        if link_request.expires_at <= datetime.now(timezone.utc):
            raise EmailVerificationCodeExpiredError()

        if link_request.attempts >= MAX_ATTEMPTS:
            raise EmailVerificationTooManyAttemptsError()

        if not verify_password(data.code, link_request.code_hash):
            attempts = (
                await self._email_identity_repository.increment_link_request_attempts(
                    link_request.id
                )
            )

            if attempts >= MAX_ATTEMPTS:
                raise EmailVerificationTooManyAttemptsError()

            raise InvalidEmailVerificationCodeError()

        # The situation may have changed while the request was pending.
        if await self._email_identity_repository.get_by_user_id(user_id):
            raise IdentityTypeConflictError()

        if await self._email_identity_repository.get_by_email(link_request.email):
            raise IdentityConflictError()

        identity = await self._email_identity_repository.create(
            EmailIdentity(
                user_id=user_id,
                email=link_request.email,
                password_hash=link_request.password_hash,
            )
        )

        await self._email_identity_repository.delete_link_request(link_request)

        return identity
