# app/google_auth/services/service_interface.py

from abc import ABC, abstractmethod

from app.sessions.schemas import TokenResponseSchema


class GoogleAuthServiceInterface(ABC):

    @abstractmethod
    async def create_authorization_url(self) -> str: ...

    @abstractmethod
    async def handle_callback(
        self,
        code: str,
        state: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema: ...
