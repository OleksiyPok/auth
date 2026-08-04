# app/auth/services/register_service.py

from app.auth.schemas import RegisterRequestSchema
from app.infrastructure.password import hash_password
from app.users.exceptions import UserAlreadyExistsError
from app.users.interfaces import UserRepositoryInterface
from app.users.models import User


class RegisterService:

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
