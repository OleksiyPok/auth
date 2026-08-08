# app/auth/services/login_service_interface.py

from abc import ABC, abstractmethod

from app.auth.schemas import LoginRequestSchema, TokenResponseSchema


class LoginServiceInterface(ABC):

    @abstractmethod
    async def login(
        self,
        data: LoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema: ...

    @abstractmethod
    async def logout(
        self,
        refresh_token: str,
    ) -> None: ...
