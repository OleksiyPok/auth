# app/auth/services/auth_session_service_interface.py

from abc import ABC, abstractmethod

from app.sessions.models import Session
from app.sessions.schemas import TokenResponseSchema


class AuthSessionServiceInterface(ABC):

    @abstractmethod
    async def create_tokens(
        self,
        user_id: str,
        provider: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema: ...

    @abstractmethod
    async def refresh_tokens(
        self,
        session: Session,
    ) -> TokenResponseSchema: ...
