# app/google_auth/service_interface.py

from abc import ABC, abstractmethod

from app.google_auth.schemas import (
    GoogleAuthorizationResponseSchema,
    GoogleConnectionStatusSchema,
)
from app.sessions.schemas import TokenResponseSchema
from app.users.models import User


class GoogleAuthServiceInterface(ABC):

    @abstractmethod
    async def create_authorization_url(
        self,
        user: User | None = None,
    ) -> str: ...

    @abstractmethod
    async def handle_callback(
        self,
        code: str,
        state: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema | None: ...

    @abstractmethod
    async def get_connection_status(
        self,
        user: User,
    ) -> GoogleConnectionStatusSchema: ...
