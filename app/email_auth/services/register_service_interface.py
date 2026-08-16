# app/email_auth/services/register_service_interface.py

from abc import ABC, abstractmethod

from app.email_auth.schemas import (
    EmailRegisterRequestSchema,
    EmailRegisterResponseSchema,
)


class EmailRegisterServiceInterface(ABC):

    @abstractmethod
    async def register(
        self,
        data: EmailRegisterRequestSchema,
    ) -> EmailRegisterResponseSchema: ...
