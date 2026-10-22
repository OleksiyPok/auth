# app/google_auth/repository/repository.py

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.google_auth.models import GoogleIdentity, GoogleOAuthState
from app.google_auth.repository.repository_interface import (
    GoogleAuthRepositoryInterface,
)


class GoogleAuthRepository(GoogleAuthRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_oauth_state(
        self,
        oauth_state: GoogleOAuthState,
    ) -> GoogleOAuthState:
        self._session.add(oauth_state)
        await self._session.flush()
        await self._session.refresh(oauth_state)

        return oauth_state

    async def get_oauth_state(
        self,
        state: str,
    ) -> GoogleOAuthState | None:
        result = await self._session.execute(
            select(GoogleOAuthState).where(
                GoogleOAuthState.state == state,
            )
        )

        return result.scalar_one_or_none()

    async def mark_oauth_state_used(
        self,
        oauth_state: GoogleOAuthState,
    ) -> GoogleOAuthState:
        oauth_state.used = True

        await self._session.flush()
        await self._session.refresh(oauth_state)

        return oauth_state

    async def get_identity_by_google_user_id(
        self,
        google_user_id: str,
    ) -> GoogleIdentity | None:
        result = await self._session.execute(
            select(GoogleIdentity).where(
                GoogleIdentity.google_user_id == google_user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_identity_by_id(
        self,
        identity_id: str,
    ) -> GoogleIdentity | None:
        result = await self._session.execute(
            select(GoogleIdentity).where(
                GoogleIdentity.id == identity_id,
            )
        )

        return result.scalar_one_or_none()

    async def create_identity(
        self,
        identity: GoogleIdentity,
    ) -> GoogleIdentity:
        self._session.add(identity)
        await self._session.flush()
        await self._session.refresh(identity)

        return identity

    async def update_identity(
        self,
        identity: GoogleIdentity,
    ) -> GoogleIdentity:
        self._session.add(identity)
        await self._session.flush()
        await self._session.refresh(identity)
        return identity

    async def get_identity_by_user_id(
        self,
        user_id: str,
    ) -> GoogleIdentity | None:
        result = await self._session.execute(
            select(GoogleIdentity).where(
                GoogleIdentity.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def delete_identity(
        self,
        identity: GoogleIdentity,
    ) -> None:
        await self._session.delete(identity)
        await self._session.flush()

    async def delete_by_user_id(self, user_id: str) -> None:
        await self._session.execute(
            delete(GoogleIdentity).where(col(GoogleIdentity.user_id) == user_id)
        )
