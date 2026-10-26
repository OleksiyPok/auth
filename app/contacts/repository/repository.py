# app/contacts/repository/repository.py

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.contacts.models import Contact
from app.contacts.repository.repository_interface import ContactRepositoryInterface


class ContactRepository(ContactRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, contact: Contact) -> Contact:
        self._session.add(contact)
        await self._session.flush()
        await self._session.refresh(contact)
        return contact

    async def get(self, user_id: str, contact_id: str) -> Contact | None:
        result = await self._session.execute(
            select(Contact).where(
                Contact.user_id == user_id,
                Contact.id == contact_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user_id(self, user_id: str) -> list[Contact]:
        result = await self._session.execute(
            select(Contact)
            .where(Contact.user_id == user_id)
            .order_by(col(Contact.created_at))
        )
        return list(result.scalars().all())

    async def delete(self, contact: Contact) -> None:
        await self._session.delete(contact)
        await self._session.flush()

    async def delete_by_user_id(self, user_id: str) -> None:
        await self._session.execute(
            delete(Contact).where(col(Contact.user_id) == user_id)
        )
