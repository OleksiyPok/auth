# app/two_factor/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.two_factor.models import TwoFactorChallenge, UserSecuritySettings


class TwoFactorRepositoryInterface(ABC):

    @abstractmethod
    async def get_settings(
        self,
        user_id: str,
        provider: str,
    ) -> UserSecuritySettings | None: ...

    @abstractmethod
    async def get_or_create_settings(
        self,
        user_id: str,
        provider: str,
    ) -> UserSecuritySettings: ...

    @abstractmethod
    async def update_settings(
        self,
        settings: UserSecuritySettings,
    ) -> UserSecuritySettings: ...

    @abstractmethod
    async def create_challenge(
        self,
        challenge: TwoFactorChallenge,
    ) -> TwoFactorChallenge: ...

    @abstractmethod
    async def get_challenge(
        self,
        challenge_id: str,
    ) -> TwoFactorChallenge | None: ...

    @abstractmethod
    async def invalidate_active_challenges(
        self,
        user_id: str,
        purpose: str,
        provider: str,
    ) -> None: ...

    @abstractmethod
    async def update_challenge(
        self,
        challenge: TwoFactorChallenge,
    ) -> TwoFactorChallenge: ...
