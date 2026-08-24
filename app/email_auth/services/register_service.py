# app/email_auth/services/register_service.py

from app.email_auth.models import EmailIdentity
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.email_auth.schemas import (
    EmailRegisterRequestSchema,
    EmailRegisterResponseSchema,
)
from app.email_auth.services.register_service_interface import (
    EmailRegisterServiceInterface,
)
from app.infrastructure.password import hash_password
from app.users.exceptions import UserAlreadyExistsError
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface


class EmailRegisterService(EmailRegisterServiceInterface):

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        email_identity_repository: EmailIdentityRepositoryInterface,
    ):
        self._user_repository = user_repository
        self._email_identity_repository = email_identity_repository

    async def register(
        self,
        data: EmailRegisterRequestSchema,
    ) -> EmailRegisterResponseSchema:
        email = data.email.strip().casefold()

        if await self._email_identity_repository.get_by_email(email):
            raise UserAlreadyExistsError()

        user = await self._user_repository.create(
            User(
                first_name=data.first_name,
                last_name=data.last_name,
            )
        )

        identity = await self._email_identity_repository.create(
            EmailIdentity(
                user_id=user.id,
                email=email,
                password_hash=hash_password(data.password),
            )
        )

        return EmailRegisterResponseSchema(
            id=user.id,
            email=identity.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )
