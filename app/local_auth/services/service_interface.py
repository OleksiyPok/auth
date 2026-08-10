# app/local_auth/services/service_interface.py

from abc import ABC, abstractmethod

from app.local_auth.models import LocalIdentity


class LocalAuthServiceInterface(ABC):

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
    ) -> LocalIdentity | None: ...

    @abstractmethod
    async def get_by_login(
        self,
        login: str,
    ) -> LocalIdentity | None: ...
