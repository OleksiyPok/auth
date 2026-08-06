# app/sessions/repository_interface.py

from abc import ABC, abstractmethod

from app.sessions.models import Session


class SessionRepositoryInterface(ABC):

    @abstractmethod
    async def create(
        self,
        session: Session,
    ) -> Session: ...

    @abstractmethod
    async def get_by_id(
        self,
        session_id: str,
    ) -> Session | None: ...

    @abstractmethod
    async def get_by_refresh_token_hash(
        self,
        refresh_token_hash: str,
    ) -> Session | None: ...

    @abstractmethod
    async def get_user_sessions(
        self,
        user_id: str,
    ) -> list[Session]: ...

    @abstractmethod
    async def get_active_user_sessions(
        self,
        user_id: str,
    ) -> list[Session]: ...

    @abstractmethod
    async def deactivate_user_sessions(
        self,
        user_id: str,
    ) -> None: ...

    @abstractmethod
    async def update(
        self,
        session: Session,
    ) -> Session: ...

    @abstractmethod
    async def delete(
        self,
        session: Session,
    ) -> None: ...
