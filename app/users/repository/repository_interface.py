# app/users/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.users.models import User
from app.users.status import UserStatus


class UserRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    async def get_all(self) -> list[User]: ...

    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def deactivate(self, user: User, status: UserStatus) -> User: ...

    @abstractmethod
    async def delete(self, user: User) -> User | None: ...

    @abstractmethod
    async def count_active_superadmins(self) -> int | None: ...
