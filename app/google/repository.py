# app/google/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.google.models import GoogleAccount, GoogleOAuthState
from app.google.repository_interface import GoogleRepositoryInterface


class GoogleRepository(GoogleRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_oauth_state(
        self,
        oauth_state: GoogleOAuthState,
    ) -> GoogleOAuthState:
        self._session.add(oauth_state)
        await self._session.commit()
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

        await self._session.commit()
        await self._session.refresh(oauth_state)

        return oauth_state

    async def get_account_by_user_id(
        self,
        user_id: str,
    ) -> GoogleAccount | None:
        result = await self._session.execute(
            select(GoogleAccount).where(
                GoogleAccount.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_account_by_google_user_id(
        self,
        google_user_id: str,
    ) -> GoogleAccount | None:
        result = await self._session.execute(
            select(GoogleAccount).where(
                GoogleAccount.google_user_id == google_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_account(
        self,
        account: GoogleAccount,
    ) -> GoogleAccount:
        self._session.add(account)

        await self._session.commit()
        await self._session.refresh(account)

        return account

    async def update_account(
        self,
        account: GoogleAccount,
    ) -> GoogleAccount:
        self._session.add(account)

        await self._session.commit()
        await self._session.refresh(account)

        return account
