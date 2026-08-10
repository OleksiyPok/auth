# app/auth/services/register_service_interface.py

from abc import ABC, abstractmethod

from app.auth.schemas import RegisterRequestSchema, RegisterResponseSchema


class RegisterServiceInterface(ABC):

    @abstractmethod
    async def register(
        self,
        data: RegisterRequestSchema,
    ) -> RegisterResponseSchema: ...
