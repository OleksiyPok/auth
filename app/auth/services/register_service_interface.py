# app/auth/services/register_service_interface.py

from abc import ABC, abstractmethod

from app.auth.schemas import RegisterRequestSchema
from app.users.models import User


class RegisterServiceInterface(ABC):

    @abstractmethod
    async def register(self, data: RegisterRequestSchema,) -> User: ...
