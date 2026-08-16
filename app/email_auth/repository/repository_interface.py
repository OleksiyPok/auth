# app/email_auth/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.email_auth.models import EmailIdentity


class EmailIdentityRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_id(self, identity_id: str) -> EmailIdentity | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> EmailIdentity | None: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> EmailIdentity | None: ...

    @abstractmethod
    async def create(self, identity: EmailIdentity) -> EmailIdentity: ...

    @abstractmethod
    async def update(self, identity: EmailIdentity) -> EmailIdentity: ...
