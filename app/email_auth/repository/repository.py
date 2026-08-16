# app/email_auth/repository/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.email_auth.models import EmailIdentity
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)


class EmailIdentityRepository(EmailIdentityRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, identity_id: str) -> EmailIdentity | None:
        result = await self._session.execute(
            select(EmailIdentity).where(EmailIdentity.id == identity_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> EmailIdentity | None:
        result = await self._session.execute(
            select(EmailIdentity).where(EmailIdentity.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> EmailIdentity | None:
        result = await self._session.execute(
            select(EmailIdentity).where(EmailIdentity.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, identity: EmailIdentity) -> EmailIdentity:
        self._session.add(identity)
        await self._session.flush()
        await self._session.refresh(identity)
        return identity

    async def update(self, identity: EmailIdentity) -> EmailIdentity:
        self._session.add(identity)
        await self._session.flush()
        await self._session.refresh(identity)
        return identity
