# app/username_auth/services/register_service.py

from app.infrastructure.password import hash_password
from app.username_auth.models import UsernameIdentity
from app.username_auth.repository.repository_interface import (
    UsernameIdentityRepositoryInterface,
)
from app.username_auth.schemas import RegisterRequestSchema, RegisterResponseSchema
from app.username_auth.services.register_service_interface import (
    UsernameRegisterServiceInterface,
)
from app.users.exceptions import UserAlreadyExistsError
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface


class UsernameRegisterService(UsernameRegisterServiceInterface):

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        local_identity_repository: UsernameIdentityRepositoryInterface,
    ):
        self._user_repository = user_repository
        self._local_identity_repository = local_identity_repository

    async def register(
        self,
        data: RegisterRequestSchema,
    ) -> RegisterResponseSchema:

        if await self._local_identity_repository.get_by_username(data.username):
            raise UserAlreadyExistsError()

        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
        )

        user = await self._user_repository.create(user)

        identity = UsernameIdentity(
            user_id=user.id,
            username=data.username,
            password_hash=hash_password(data.password),
        )

        await self._local_identity_repository.create(identity)

        return RegisterResponseSchema(
            id=user.id,
            username=identity.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )
