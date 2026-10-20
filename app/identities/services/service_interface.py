# app/identities/services/service_interface.py

from abc import ABC, abstractmethod

from app.email_auth.models import EmailIdentity
from app.google_auth.models import GoogleIdentity
from app.username_auth.models import UsernameIdentity

class IdentityServiceInterface(ABC):

    @abstractmethod
    async def list_identities(
            self,
            user_id: str,
    ) -> list[EmailIdentity | UsernameIdentity | GoogleIdentity]: ...

    @abstractmethod
    async def get_owner_id(
        self,
        identity_type: str,
        identity_id: str,
    ) -> str | None: ...

    @abstractmethod
    async def get_identity(
        self,
        identity_id: str,
    ) -> EmailIdentity | UsernameIdentity | GoogleIdentity | None: ...

    @abstractmethod
    async def delete_identity(
        self,
        identity: EmailIdentity | UsernameIdentity | GoogleIdentity,
    ) -> None: ...

    @abstractmethod
    async def transfer_identity(
        self,
        identity: EmailIdentity | UsernameIdentity | GoogleIdentity,
        new_user_id: str,
    ) -> EmailIdentity | UsernameIdentity | GoogleIdentity: ...