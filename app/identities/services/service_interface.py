# app/identities/services/service_interface.py

from abc import ABC, abstractmethod


class IdentityServiceInterface(ABC):

    @abstractmethod
    async def get_owner_id(
        self,
        identity_type: str,
        identity_id: str,
    ) -> str | None: ...
