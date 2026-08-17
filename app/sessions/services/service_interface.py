# app/sessions/services/service_interface.py

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional

from app.sessions.models import Session
from app.users.models import User


class SessionServiceInterface(ABC):

    @abstractmethod
    async def create_session(
        self,
        user_id: str,
        refresh_token: str,
        expires_delta: timedelta,
        provider: str = "username",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Session: ...

    @abstractmethod
    async def get_by_id(
        self,
        session_id: str,
    ) -> Optional[Session]: ...

    @abstractmethod
    async def get_by_refresh_token(
        self,
        refresh_token: str,
    ) -> Optional[Session]: ...

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
    async def revoke_session(
        self,
        session_id: str,
    ) -> None: ...

    @abstractmethod
    async def validate_refresh_token(
        self,
        refresh_token: str,
    ) -> Session: ...

    @abstractmethod
    async def revoke_all_sessions(
        self,
        user: User,
    ) -> None: ...

    @abstractmethod
    async def validate_session(
        self,
        session_id: str,
    ) -> Session: ...

    @abstractmethod
    async def logout(
        self,
        user: User,
    ) -> None: ...
