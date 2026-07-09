# app/users/service.py

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
