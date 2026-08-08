# app/google/service_interface.py

from abc import ABC, abstractmethod

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
