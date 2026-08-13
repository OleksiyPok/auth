# app/local_auth/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.local_auth.models import LocalIdentity


class LocalIdentityRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        identity_id: str,
    ) -> LocalIdentity | None: ...

    @abstractmethod
    async def get_by_login(
        self,
        login: str,
    ) -> LocalIdentity | None: ...

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
    ) -> LocalIdentity | None: ...

    @abstractmethod
    async def create(
        self,
        identity: LocalIdentity,
    ) -> LocalIdentity: ...
