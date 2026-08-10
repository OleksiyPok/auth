# app/local_auth/services/login_service_interface.py

from abc import ABC, abstractmethod

from app.auth.schemas import TokenResponseSchema
from app.local_auth.schemas import LoginRequestSchema


class LocalLoginServiceInterface(ABC):

    @abstractmethod
    async def login(
        self,
        data: LoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema: ...
