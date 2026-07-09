# app/users/interfaces.py

from abc import ABC, abstractmethod

from app.users.models import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    async def get_by_login(self, login: str) -> User | None: ...

    @abstractmethod
    async def get_all(self) -> list[User]: ...
