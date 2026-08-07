# app/users/service_interface.py

from abc import ABC, abstractmethod

from app.users.models import User
from app.users.schemas import UserRoleAssignRequestSchema, UserUpdateRequestSchema


class UserServiceInterface(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User: ...

    @abstractmethod
    async def get_by_login(self, login: str) -> User: ...

    @abstractmethod
    async def get_all(self) -> list[User]: ...

    @abstractmethod
    async def update_self(self, user: User, data: UserUpdateRequestSchema) -> User: ...

    @abstractmethod
    async def delete(self, user_id: str) -> User: ...

    @abstractmethod
    async def change_role(
        self, user_id: str, role_data: UserRoleAssignRequestSchema, current_user_id: str
    ) -> User: ...

    @abstractmethod
    async def deactivate_user(
        self,
        current_user: User,
        target_user: User,
    ) -> User: ...
