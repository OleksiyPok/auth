# app/email_auth/services/register_service.py

import secrets
from datetime import datetime, timedelta, timezone

from app.email_auth.exceptions import (
    EmailRegistrationNotFoundError,
    EmailVerificationCodeExpiredError,
    EmailVerificationTooManyAttemptsError,
    InvalidEmailVerificationCodeError,
)
from app.email_auth.models import EmailIdentity, EmailRegistration
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.email_auth.schemas import (
    EmailRegisterChallengeResponseSchema,
    EmailRegisterConfirmRequestSchema,
    EmailRegisterRequestSchema,
    EmailRegisterResponseSchema,
)
from app.email_auth.services.register_service_interface import (
    EmailRegisterServiceInterface,
)
from app.infrastructure.email.base import EmailService
from app.infrastructure.password import hash_password, verify_password
from app.two_factor.config import settings as fa_settings
from app.users.exceptions import UserAlreadyExistsError
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface

CHALLENGE_EXPIRE_MINUTES = fa_settings.CHALLENGE_EXPIRE_MINUTES
MAX_ATTEMPTS = fa_settings.MAX_ATTEMPTS
CODE_LENGTH = fa_settings.CODE_LENGTH


class EmailRegisterService(EmailRegisterServiceInterface):

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        email_identity_repository: EmailIdentityRepositoryInterface,
        email_service: EmailService,
    ):
        self._user_repository = user_repository
        self._email_identity_repository = email_identity_repository
        self._email_service = email_service

    async def register(
        self,
        data: EmailRegisterRequestSchema,
    ) -> EmailRegisterChallengeResponseSchema:
        email = data.email.strip().casefold()

        if await self._email_identity_repository.get_by_email(email):
            raise UserAlreadyExistsError()

        # A pending registration does not reserve the address:
        # a new request replaces the previous one.
        await self._email_identity_repository.delete_registrations_by_email(email)

        code = f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"
        registration = await self._email_identity_repository.create_registration(
            EmailRegistration(
                email=email,
                first_name=data.first_name,
                last_name=data.last_name,
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
            subject="Confirm your email registration",
            body=(
                f"Your verification code is: {code}\n\n"
                f"The code expires in {CHALLENGE_EXPIRE_MINUTES} minutes."
            ),
        )

        return EmailRegisterChallengeResponseSchema(
            registration_id=registration.id,
            expires_at=registration.expires_at.isoformat(),
        )

    async def confirm(
        self,
        data: EmailRegisterConfirmRequestSchema,
    ) -> EmailRegisterResponseSchema:
        registration = await self._email_identity_repository.get_registration(
            data.registration_id
        )

        if not registration:
            raise EmailRegistrationNotFoundError()

        if registration.expires_at <= datetime.now(timezone.utc):
            raise EmailVerificationCodeExpiredError()

        if registration.attempts >= MAX_ATTEMPTS:
            raise EmailVerificationTooManyAttemptsError()

        if not verify_password(data.code, registration.code_hash):
            attempts = (
                await self._email_identity_repository.increment_registration_attempts(
                    registration.id
                )
            )

            if attempts >= MAX_ATTEMPTS:
                raise EmailVerificationTooManyAttemptsError()

            raise InvalidEmailVerificationCodeError()

        # The address may have been taken while the registration was pending.
        if await self._email_identity_repository.get_by_email(registration.email):
            raise UserAlreadyExistsError()

        user = await self._user_repository.create(
            User(
                first_name=registration.first_name,
                last_name=registration.last_name,
            )
        )

        identity = await self._email_identity_repository.create(
            EmailIdentity(
                user_id=user.id,
                email=registration.email,
                password_hash=registration.password_hash,
            )
        )

        await self._email_identity_repository.delete_registration(registration)

        return EmailRegisterResponseSchema(
            id=user.id,
            email=identity.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )