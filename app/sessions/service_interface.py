# app/sessions/service_interface.py

from datetime import timedelta
from typing import Optional

from app.sessions.models import Session
from app.users.models import User


class SessionServiceInterface:

    async def create_session(
        self,
        user_id: str,
        refresh_token: str,
        expires_delta: timedelta,
        provider: str = "local",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Session: ...

    async def get_by_id(
        self,
        session_id: str,
    ) -> Optional[Session]: ...

    async def get_by_refresh_token(
        self,
        refresh_token: str,
    ) -> Optional[Session]: ...

    async def rotate_refresh_token(
        self,
        session: Session,
        new_refresh_token: str,
        expires_delta: timedelta,
    ) -> Session: ...

    async def get_user_sessions(
        self,
        user_id: str,
    ) -> list[Session]: ...

    async def revoke(
        self,
        session: Session,
    ) -> None: ...

    async def revoke_session(
        self,
        session_id: str,
    ) -> None: ...

    async def validate_refresh_token(
        self,
        refresh_token: str,
    ) -> Session: ...

    async def revoke_all_sessions(
        self,
        user: User,
    ) -> None: ...

    async def validate_session(
        self,
        session_id: str,
    ) -> Session: ...
