# app/username_auth/services/login_service_interface.py

from abc import ABC, abstractmethod

from app.username_auth.schemas import LoginRequestSchema
from app.sessions.schemas import AuthenticationResponseSchema


class LocalLoginServiceInterface(ABC):

    @abstractmethod
    async def login(
        self,
        data: LoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema: ...
