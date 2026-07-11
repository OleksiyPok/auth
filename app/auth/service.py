# app/auth/service.py

from fastapi import HTTPException

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
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "USER_ALREADY_EXISTS",
                    "message": "User already exists",
                },
            )

        user = User(login=data.login)

        user = await self._repository.create(user)

        return RegisterResponseSchema(
            id=user.id,
            login=user.login,
        )
