# app/email_auth/services/register_service_interface.py

from abc import ABC, abstractmethod

from app.email_auth.schemas import (
    EmailRegisterChallengeResponseSchema,
    EmailRegisterConfirmRequestSchema,
    EmailRegisterRequestSchema,
    EmailRegisterResendRequestSchema,
    EmailRegisterResponseSchema,
)


class EmailRegisterServiceInterface(ABC):

    @abstractmethod
    async def register(
        self,
        data: EmailRegisterRequestSchema,
    ) -> EmailRegisterChallengeResponseSchema: ...

    @abstractmethod
    async def resend(
        self,
        data: EmailRegisterResendRequestSchema,
    ) -> EmailRegisterChallengeResponseSchema: ...

    @abstractmethod
    async def confirm(
        self,
        data: EmailRegisterConfirmRequestSchema,
    ) -> EmailRegisterResponseSchema: ...
