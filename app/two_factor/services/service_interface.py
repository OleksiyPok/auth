# app/two_factor/services/service_interface.py

from abc import ABC, abstractmethod

from app.sessions.schemas import AuthenticationResponseSchema
from app.two_factor.schemas import (
    TwoFactorChallengeResponseSchema,
    TwoFactorMethodSchema,
)
from app.users.models import User


class TwoFactorServiceInterface(ABC):

    @abstractmethod
    async def is_enabled(
        self,
        user_id: str,
    ) -> bool: ...

    @abstractmethod
    async def get_methods(
        self,
        user_id: str,
    ) -> list[TwoFactorMethodSchema]: ...

    @abstractmethod
    async def authenticate_or_challenge(
        self,
        user: User,
        identity_id: str,
        identity_type: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema: ...

    @abstractmethod
    async def confirm_login(
        self,
        challenge_id: str,
        code: str,
    ) -> AuthenticationResponseSchema: ...

    @abstractmethod
    async def request_enable(
        self,
        user: User,
    ) -> TwoFactorChallengeResponseSchema: ...

    @abstractmethod
    async def confirm_enable(
        self,
        user: User,
        challenge_id: str,
        code: str,
    ) -> None: ...

    @abstractmethod
    async def request_disable(
        self,
        user: User,
    ) -> TwoFactorChallengeResponseSchema: ...

    @abstractmethod
    async def confirm_disable(
        self,
        user: User,
        challenge_id: str,
        code: str,
    ) -> None: ...

    @abstractmethod
    async def request_merge_challenge(
        self,
        user: User,
    ) -> TwoFactorChallengeResponseSchema: ...

    @abstractmethod
    async def confirm_merge_challenge(
        self,
        user_id: str,
        challenge_id: str,
        code: str,
    ) -> None: ...
