# app/google_auth/services/service_interface.py

from abc import ABC, abstractmethod

from app.google_auth.purpose import GoogleOAuthPurpose
from app.google_auth.schemas import GoogleCallbackResponse


class GoogleAuthServiceInterface(ABC):

    @abstractmethod
    async def create_authorization_url(
        self,
        purpose: GoogleOAuthPurpose = GoogleOAuthPurpose.LOGIN,
        user_id: str | None = None,
    ) -> str: ...

    @abstractmethod
    async def handle_callback(
        self,
        code: str,
        state: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> GoogleCallbackResponse: ...
