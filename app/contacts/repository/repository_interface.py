# app/contacts/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.contacts.models import Contact


class ContactRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, contact: Contact) -> Contact: ...

    @abstractmethod
    async def get(self, user_id: str, contact_id: str) -> Contact | None: ...

    @abstractmethod
    async def list_by_user_id(self, user_id: str) -> list[Contact]: ...

    @abstractmethod
    async def move_to_user(self, from_user_id: str, to_user_id: str) -> None: ...

    @abstractmethod
    async def delete(self, contact: Contact) -> None: ...

    @abstractmethod
    async def delete_by_user_id(self, user_id: str) -> None: ...
