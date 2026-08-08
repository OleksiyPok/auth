# app/auth/services/register_service.py

from app.auth.schemas import RegisterRequestSchema
from app.auth.services.register_service_interface import RegisterServiceInterface
from app.infrastructure.password import hash_password
from app.users.exceptions import UserAlreadyExistsError
from app.users.models import User
from app.users.repository_interface import UserRepositoryInterface


class RegisterService(RegisterServiceInterface):

    def __init__(
        self,
        repository: UserRepositoryInterface,
    ):
        self._repository = repository

    async def register(
        self,
        data: RegisterRequestSchema,
    ) -> User:
        if await self._repository.get_by_login(data.login):
            raise UserAlreadyExistsError()

        user = User(
            login=data.login,
            password_hash=hash_password(data.password),
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )

        return await self._repository.create(user)
