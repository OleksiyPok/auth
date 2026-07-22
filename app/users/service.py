# app/users/service.py

from fastapi import HTTPException

from app.users.interfaces import UserRepositoryInterface
from app.users.models import User
from app.users.schemas import UserUpdateByAdminRequestSchema, UserUpdateRequestSchema


class UserService:

    def __init__(
        self,
        repository: UserRepositoryInterface,
    ):
        self._repository = repository

    async def get_by_id(self, user_id: str) -> User:
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

    async def get_by_login(self, login: str) -> User:
        user = await self._repository.get_by_login(login)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found",
                },
            )

        return user

    async def get_all(self) -> list[User]:
        return await self._repository.get_all()

    async def update_self(self, user: User, data: UserUpdateRequestSchema) -> User:

        return await self._update(user, data)

    async def update_by_admin(
        self, user_id: str, data: UserUpdateByAdminRequestSchema
    ) -> User:
        user = await self.get_by_id(user_id)

        return await self._update(user, data)

    async def delete(self, user_id: str) -> User:
        user = await self.get_by_id(user_id)

        return await self._repository.delete(user)

    async def _update(
        self,
        user: User,
        data: UserUpdateRequestSchema | UserUpdateByAdminRequestSchema,
    ) -> User:

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user, key, value)

        return await self._repository.update(user)
