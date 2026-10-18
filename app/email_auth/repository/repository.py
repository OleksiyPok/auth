# app/email_auth/repository/repository.py

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.email_auth.models import EmailIdentity, EmailRegistration
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


    async def create_registration(
        self, registration: EmailRegistration
    ) -> EmailRegistration:
        self._session.add(registration)
        await self._session.flush()
        await self._session.refresh(registration)
        return registration

    async def get_registration(self, registration_id: str) -> EmailRegistration | None:
        result = await self._session.execute(
            select(EmailRegistration).where(EmailRegistration.id == registration_id)
        )
        return result.scalar_one_or_none()

    async def update_registration(
        self, registration: EmailRegistration
    ) -> EmailRegistration:
        self._session.add(registration)
        await self._session.flush()
        await self._session.refresh(registration)
        return registration

    async def delete_registration(self, registration: EmailRegistration) -> None:
        await self._session.delete(registration)
        await self._session.flush()

    async def delete_registrations_by_email(self, email: str) -> None:
        await self._session.execute(
            delete(EmailRegistration).where(EmailRegistration.email == email)
        )