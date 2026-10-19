# app/username_auth/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.username_auth.models import UsernameIdentity


class UsernameIdentityRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        identity_id: str,
    ) -> UsernameIdentity | None: ...

    @abstractmethod
    async def get_by_username(
        self,
        username: str,
    ) -> UsernameIdentity | None: ...

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
    ) -> UsernameIdentity | None: ...

    @abstractmethod
    async def create(
        self,
        identity: UsernameIdentity,
    ) -> UsernameIdentity: ...

    @abstractmethod
    async def update(
        self,
        identity: UsernameIdentity,
    ) -> UsernameIdentity: ...

    @abstractmethod
    async def delete(
        self,
        identity: UsernameIdentity,
    ) -> None: ...