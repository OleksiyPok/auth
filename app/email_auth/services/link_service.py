# app/email_auth/services/link_service.py

import secrets
from datetime import datetime, timedelta, timezone

from app.core.identifiers import normalize_email
from app.email_auth.models import EmailLinkRequest
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.email_auth.schemas import (
    EmailLinkChallengeResponseSchema,
    EmailLinkRequestSchema,
)
from app.email_auth.services.link_service_interface import EmailLinkServiceInterface
from app.identities.exceptions import IdentityConflictError, IdentityTypeConflictError
from app.infrastructure.email.base import EmailService
from app.infrastructure.password import hash_password
from app.two_factor.config import settings as fa_settings

CHALLENGE_EXPIRE_MINUTES = fa_settings.CHALLENGE_EXPIRE_MINUTES
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
