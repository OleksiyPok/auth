# app/username_auth/services/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.username_auth.models import LocalIdentity
from app.username_auth.services.repository_interface import (
    LocalIdentityRepositoryInterface,
)


class LocalIdentityRepository(LocalIdentityRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(
        self,
        identity_id: str,
    ) -> LocalIdentity | None:
        result = await self._session.execute(
            select(LocalIdentity).where(
                LocalIdentity.id == identity_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_login(
        self,
        login: str,
    ) -> LocalIdentity | None:
        result = await self._session.execute(
            select(LocalIdentity).where(
                LocalIdentity.login == login,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: str,
    ) -> LocalIdentity | None:
        result = await self._session.execute(
            select(LocalIdentity).where(
                LocalIdentity.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        identity: LocalIdentity,
    ) -> LocalIdentity:
        self._session.add(identity)
        await self._session.flush()
        await self._session.refresh(identity)
        return identity
