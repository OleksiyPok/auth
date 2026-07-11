# app/users/service.py

from fastapi import HTTPException

from app.users.interfaces import UserRepositoryInterface
from app.users.models import User


class UserService:

    def __init__(
        self,
        repository: UserRepositoryInterface,
    ):
        self._repository = repository

    async def get_all(self) -> list[User]:
        return await self._repository.get_all()

    async def get_by_id(
        self,
        user_id: str,
    ) -> User:
        user = await self._repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found",
                },
            )

        return user

    async def delete(
        self,
        user_id: str,
    ) -> User:
        user = await self._repository.delete(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found",
                },
            )

        return user
