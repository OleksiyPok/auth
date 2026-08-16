# app/username_auth/services/repository_interface.py

from abc import ABC, abstractmethod

from app.username_auth.models import UsernameIdentity


class UsernameIdentityRepositoryInterface(ABC):

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
