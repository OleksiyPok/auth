# app/email_auth/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.email_auth.models import EmailIdentity, EmailRegistration


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

    @abstractmethod
    async def delete(self, identity: EmailIdentity) -> None: ...

    @abstractmethod
    async def create_registration(
        self, registration: EmailRegistration
    ) -> EmailRegistration: ...

    @abstractmethod
    async def get_registration(
        self, registration_id: str
    ) -> EmailRegistration | None: ...

    @abstractmethod
    async def update_registration(
        self, registration: EmailRegistration
    ) -> EmailRegistration: ...

    @abstractmethod
    async def increment_registration_attempts(self, registration_id: str) -> int: ...

    @abstractmethod
    async def delete_registration(self, registration: EmailRegistration) -> None: ...

    @abstractmethod
    async def delete_by_user_id(self, user_id: str) -> None: ...

    @abstractmethod
    async def delete_registrations_by_email(self, email: str) -> None: ...
