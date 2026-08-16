# app/username_auth/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.username_auth.models import UsernameIdentity


class LocalIdentityRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        identity_id: str,
    ) -> UsernameIdentity | None: ...

    @abstractmethod
    async def get_by_login(
        self,
        login: str,
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
