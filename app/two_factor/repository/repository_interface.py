# app/two_factor/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.two_factor.models import (
    RecoveryCode,
    TwoFactorChallenge,
    TwoFactorMethod,
    UserSecuritySettings,
)


class TwoFactorRepositoryInterface(ABC):

    @abstractmethod
    async def get_settings(
        self,
        user_id: str,
    ) -> UserSecuritySettings | None: ...

    @abstractmethod
    async def get_or_create_settings(
        self,
        user_id: str,
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
    ) -> None: ...

    @abstractmethod
    async def update_challenge(
        self,
        challenge: TwoFactorChallenge,
    ) -> TwoFactorChallenge: ...

    @abstractmethod
    async def increment_challenge_attempts(self, challenge_id: str) -> int: ...

    @abstractmethod
    async def create_method(self, method: TwoFactorMethod) -> TwoFactorMethod: ...

    @abstractmethod
    async def list_methods(self, user_id: str) -> list[TwoFactorMethod]: ...

    @abstractmethod
    async def get_method(
        self,
        user_id: str,
        method_id: str,
    ) -> TwoFactorMethod | None: ...

    @abstractmethod
    async def update_method(self, method: TwoFactorMethod) -> TwoFactorMethod: ...

    @abstractmethod
    async def delete_challenges_by_method_id(self, method_id: str) -> None: ...

    @abstractmethod
    async def delete_method(self, method: TwoFactorMethod) -> None: ...

    @abstractmethod
    async def delete_expired_or_used_challenges(self) -> None: ...

    @abstractmethod
    async def replace_recovery_codes(
        self,
        user_id: str,
        code_hashes: list[str],
    ) -> None: ...

    @abstractmethod
    async def get_unused_recovery_code(
        self,
        user_id: str,
        code_hash: str,
    ) -> RecoveryCode | None: ...

    @abstractmethod
    async def update_recovery_code(self, code: RecoveryCode) -> RecoveryCode: ...

    @abstractmethod
    async def delete_recovery_codes(self, user_id: str) -> None: ...

    @abstractmethod
    async def delete_by_user_id(self, user_id: str) -> None: ...
