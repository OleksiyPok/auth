# app/auth/service.py

from app.auth.schemas import RegisterRequestSchema, RegisterResponseSchema
from app.users.interfaces import UserRepositoryInterface
from app.users.models import User


class AuthService:

    def __init__(
        self,
        repository: UserRepositoryInterface,
    ):
        self._repository = repository

    async def register(
        self,
        data: RegisterRequestSchema,
    ) -> RegisterResponseSchema:

        if await self._repository.get_by_login(data.login):
            raise ValueError("This user already exists.")

        user = User(login=data.login)

        user = await self._repository.create(user)

        return RegisterResponseSchema(
            id=user.id,
            login=user.login,
        )
