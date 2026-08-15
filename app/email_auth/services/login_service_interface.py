from abc import ABC, abstractmethod

from app.email_auth.schemas import EmailLoginRequestSchema
from app.sessions.schemas import AuthenticationResponseSchema


class EmailLoginServiceInterface(ABC):

    @abstractmethod
    async def login(
        self,
        data: EmailLoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema: ...
