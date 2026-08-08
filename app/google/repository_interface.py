# app/google/repository_interface.py

from abc import ABC, abstractmethod

from app.google.models import GoogleAccount, GoogleOAuthState


class GoogleRepositoryInterface(ABC):

    @abstractmethod
    async def create_oauth_state(
        self,
        oauth_state: GoogleOAuthState,
    ) -> GoogleOAuthState: ...

    @abstractmethod
    async def get_oauth_state(
        self,
        state: str,
    ) -> GoogleOAuthState | None: ...

    @abstractmethod
    async def mark_oauth_state_used(
        self,
        oauth_state: GoogleOAuthState,
    ) -> GoogleOAuthState: ...

    @abstractmethod
    async def get_account_by_user_id(
        self,
        user_id: str,
    ) -> GoogleAccount | None: ...

    @abstractmethod
    async def get_account_by_google_user_id(
        self,
        google_user_id: str,
    ) -> GoogleAccount | None: ...

    @abstractmethod
    async def create_account(
        self,
        account: GoogleAccount,
    ) -> GoogleAccount: ...

    @abstractmethod
    async def update_account(
        self,
        account: GoogleAccount,
    ) -> GoogleAccount: ...
