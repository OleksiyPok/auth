# app/google/service_interface.py

from abc import ABC, abstractmethod

from app.google.schemas import (
    GoogleConnectionStatusSchema,
    GoogleContactCreateSchema,
    GoogleContactResponseSchema,
    GoogleContactUpdateSchema,
)
from app.users.models import User


class GoogleServiceInterface(ABC):

    @abstractmethod
    async def create_authorization_url(
        self,
        user: User,
    ) -> str: ...

    @abstractmethod
    async def handle_callback(
        self,
        code: str,
        state: str,
    ) -> None: ...

    @abstractmethod
    async def get_connection_status(
        self,
        user: User,
    ) -> GoogleConnectionStatusSchema: ...

    @abstractmethod
    async def get_contacts(
        self,
        user: User,
    ) -> list[GoogleContactResponseSchema]: ...

    @abstractmethod
    async def get_contact(
        self,
        user: User,
        resource_name: str,
    ) -> GoogleContactResponseSchema: ...

    @abstractmethod
    async def create_contact(
        self,
        user: User,
        data: GoogleContactCreateSchema,
    ) -> GoogleContactResponseSchema: ...

    @abstractmethod
    async def update_contact(
        self,
        user: User,
        resource_name: str,
        data: GoogleContactUpdateSchema,
    ) -> GoogleContactResponseSchema: ...

    @abstractmethod
    async def delete_contact(
        self,
        user: User,
        resource_name: str,
    ) -> None: ...
