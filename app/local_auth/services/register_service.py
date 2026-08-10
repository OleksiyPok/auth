# app/local_auth/services/register_service.py

from app.infrastructure.password import hash_password
from app.local_auth.models import LocalIdentity
from app.local_auth.schemas import RegisterRequestSchema, RegisterResponseSchema
from app.local_auth.services.register_service_interface import (
    LocalRegisterServiceInterface,
)
from app.local_auth.services.repository_interface import (
    LocalIdentityRepositoryInterface,
)
from app.users.exceptions import UserAlreadyExistsError
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface


class LocalRegisterService(LocalRegisterServiceInterface):

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        local_identity_repository: LocalIdentityRepositoryInterface,
    ):
        self._user_repository = user_repository
        self._local_identity_repository = local_identity_repository

    async def register(
        self,
        data: RegisterRequestSchema,
    ) -> RegisterResponseSchema:

        if await self._local_identity_repository.get_by_login(data.login):
            raise UserAlreadyExistsError()

        user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )

        user = await self._user_repository.create(user)

        identity = LocalIdentity(
            user_id=user.id,
            login=data.login,
            password_hash=hash_password(data.password),
        )

        await self._local_identity_repository.create(identity)

        await self._user_repository.commit()

        return RegisterResponseSchema(
            id=user.id,
            login=identity.login,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )
