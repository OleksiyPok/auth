# app/auth/services/token_service_interface.py

from abc import ABC, abstractmethod

from app.auth.schemas import TokenResponseSchema
from app.users.models import User


class TokenServiceInterface(ABC):

    @abstractmethod
    async def authenticate(
        self,
        token: str,
    ) -> User: ...

    @abstractmethod
    async def refresh(
        self,
        refresh_token: str,
    ) -> TokenResponseSchema: ...
