# app/email_auth/repository/repository.py

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.db.session import session_factory
from app.email_auth.models import EmailIdentity, EmailLinkRequest, EmailRegistration
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

    async def delete(self, identity: EmailIdentity) -> None:
        await self._session.delete(identity)
        await self._session.flush()

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

    # noinspection PyMethodMayBeStatic
    async def increment_registration_attempts(self, registration_id: str) -> int:
        # Separate transaction: the counter must survive the rollback of the
        # request transaction that happens when the service raises an error.
        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    update(EmailRegistration)
                    .where(col(EmailRegistration.id) == registration_id)
                    .values(attempts=EmailRegistration.attempts + 1)
                )
                result = await session.execute(
                    select(EmailRegistration.attempts).where(
                        EmailRegistration.id == registration_id
                    )
                )
                return result.scalar_one()

    async def delete_registration(self, registration: EmailRegistration) -> None:
        await self._session.delete(registration)
        await self._session.flush()

    async def delete_registrations_by_email(self, email: str) -> None:
        await self._session.execute(
            delete(EmailRegistration).where(col(EmailRegistration.email) == email)
        )

    async def delete_by_user_id(self, user_id: str) -> None:
        await self._session.execute(
            delete(EmailLinkRequest).where(col(EmailLinkRequest.user_id) == user_id)
        )
        await self._session.execute(
            delete(EmailIdentity).where(col(EmailIdentity.user_id) == user_id)
        )

    async def create_link_request(
        self, link_request: EmailLinkRequest
    ) -> EmailLinkRequest:
        self._session.add(link_request)
        await self._session.flush()
        await self._session.refresh(link_request)
        return link_request

    async def delete_link_requests_by_user_id(self, user_id: str) -> None:
        await self._session.execute(
            delete(EmailLinkRequest).where(col(EmailLinkRequest.user_id) == user_id)
        )
