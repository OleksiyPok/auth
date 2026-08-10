# app/local_auth/services/register_service_interface.py

from abc import ABC, abstractmethod

from app.local_auth.schemas import RegisterRequestSchema, RegisterResponseSchema


class LocalRegisterServiceInterface(ABC):

    @abstractmethod
    async def register(
        self,
        data: RegisterRequestSchema,
    ) -> RegisterResponseSchema: ...
