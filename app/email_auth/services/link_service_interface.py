# app/email_auth/services/link_service_interface.py

from abc import ABC, abstractmethod

from app.email_auth.models import EmailIdentity
from app.email_auth.schemas import (
    EmailLinkChallengeResponseSchema,
    EmailLinkConfirmRequestSchema,
    EmailLinkRequestSchema,
)


class EmailLinkServiceInterface(ABC):

    @abstractmethod
    async def request_link(
        self,
        user_id: str,
        data: EmailLinkRequestSchema,
    ) -> EmailLinkChallengeResponseSchema: ...

    @abstractmethod
    async def confirm_link(
        self,
        user_id: str,
        data: EmailLinkConfirmRequestSchema,
    ) -> EmailIdentity: ...
