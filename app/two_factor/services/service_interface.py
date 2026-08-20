# app/two_factor/services/service_interface.py

from abc import ABC, abstractmethod

from app.sessions.schemas import AuthenticationResponseSchema
from app.two_factor.schemas import TwoFactorChallengeResponseSchema
from app.users.models import User


class TwoFactorServiceInterface(ABC):

    @abstractmethod
    async def is_enabled(
        self,
        user_id: str,
        provider: str,
    ) -> bool: ...

    @abstractmethod
    async def authenticate_or_challenge(
        self,
        user: User,
        identity_id: str,
        email: str,
        provider: str,
        two_factor_enabled: bool,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema: ...

    @abstractmethod
    async def confirm_login(
        self,
        challenge_id: str,
        code: str,
        provider: str,
    ) -> AuthenticationResponseSchema: ...

    @abstractmethod
    async def request_enable(
        self,
        user: User,
        identity_id: str,
        email: str,
        provider: str,
    ) -> TwoFactorChallengeResponseSchema: ...

    @abstractmethod
    async def confirm_enable(
        self,
        user: User,
        email: str,
        challenge_id: str,
        code: str,
        provider: str,
    ) -> None: ...

    @abstractmethod
    async def request_disable(
        self,
        user: User,
        identity_id: str,
        email: str,
        provider: str,
    ) -> TwoFactorChallengeResponseSchema: ...

    @abstractmethod
    async def confirm_disable(
        self,
        user: User,
        email: str,
        challenge_id: str,
        code: str,
        provider: str,
    ) -> None: ...
