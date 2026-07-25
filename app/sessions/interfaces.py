# app/sessions/interfaces.py

from abc import ABC, abstractmethod
from datetime import timedelta

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


class SessionServiceInterface(ABC):

    @abstractmethod
    async def create_session(
        self,
        user_id: str,
        refresh_token: str,
        expires_delta: timedelta,
        provider: str = "local",
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session: ...

    @abstractmethod
    async def get_by_id(
        self,
        session_id: str,
    ) -> Session | None: ...

    @abstractmethod
    async def get_by_refresh_token(
        self,
        refresh_token: str,
    ) -> Session | None: ...

    @abstractmethod
    async def rotate_refresh_token(
        self,
        session: Session,
        new_refresh_token: str,
        expires_delta: timedelta,
    ) -> Session: ...

    @abstractmethod
    async def get_user_sessions(
        self,
        user_id: str,
    ) -> list[Session]: ...

    @abstractmethod
    async def revoke(
        self,
        session: Session,
    ) -> None: ...

    @abstractmethod
    async def revoke_session_for_user(
        self,
        session_id: str,
        user_id: str,
    ) -> None: ...

    @abstractmethod
    async def validate_refresh_token(
        self,
        refresh_token: str,
    ) -> Session: ...

    @abstractmethod
    async def revoke_all_sessions(
        self,
        user_id: str,
    ) -> None: ...

    @abstractmethod
    async def validate_session(
        self,
        session_id: str,
    ) -> Session: ...
