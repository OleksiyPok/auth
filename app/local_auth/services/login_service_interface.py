from abc import ABC, abstractmethod

from app.local_auth.schemas import LoginRequestSchema
from app.sessions.schemas import AuthenticationResponseSchema


class LocalLoginServiceInterface(ABC):

    @abstractmethod
    async def login(
        self,
        data: LoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema: ...
