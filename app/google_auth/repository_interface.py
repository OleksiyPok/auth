# app/google_auth/repository_interface.py

from abc import ABC, abstractmethod

from app.google_auth.models import GoogleIdentity, GoogleOAuthState


class GoogleAuthRepositoryInterface(ABC):

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
    async def get_identity_by_google_user_id(
        self,
        google_user_id: str,
    ) -> GoogleIdentity | None: ...

    @abstractmethod
    async def create_identity(
        self,
        identity: GoogleIdentity,
    ) -> GoogleIdentity: ...
