# app/sessions/service.py

from datetime import datetime, timedelta, timezone

from app.core.refresh_token import hash_refresh_token
from app.sessions.exceptions import (
    InvalidRefreshTokenError,
    SessionAccessDeniedError,
    SessionExpiredError,
    SessionNotFoundError,
    SessionRevokedError,
)
from app.sessions.interfaces import SessionRepositoryInterface, SessionServiceInterface
from app.sessions.models import Session


class SessionService(SessionServiceInterface):

    def __init__(
        self,
        repository: SessionRepositoryInterface,
    ):
        self._repository = repository

    async def create_session(
        self,
        user_id: str,
        refresh_token: str,
        expires_delta: timedelta,
        provider: str = "local",
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:
        now = datetime.now(timezone.utc)

        session = Session(
            user_id=user_id,
            provider=provider,
            refresh_token_hash=hash_refresh_token(refresh_token),
            expires_at=now + expires_delta,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=now,
            updated_at=now,
            last_used_at=now,
        )

        return await self._repository.create(session)

    async def get_by_id(
        self,
        session_id: str,
    ) -> Session | None:

        return await self._repository.get_by_id(
            session_id,
        )

    async def get_by_refresh_token(
        self,
        refresh_token: str,
    ) -> Session | None:
        token_hash = hash_refresh_token(refresh_token)

        return await self._repository.get_by_refresh_token_hash(token_hash)

    async def rotate_refresh_token(
        self,
        session: Session,
        new_refresh_token: str,
        expires_delta: timedelta,
    ) -> Session:
        now = datetime.now(timezone.utc)

        session.refresh_token_hash = hash_refresh_token(new_refresh_token)
        session.last_used_at = now
        session.updated_at = now
        session.expires_at = now + expires_delta

        return await self._repository.update(session)

    async def get_user_sessions(
        self,
        user_id: str,
    ) -> list[Session]:

        return await self._repository.get_active_user_sessions(
            user_id,
        )

    async def revoke(
        self,
        session: Session,
    ) -> None:
        now = datetime.now(timezone.utc)

        session.is_active = False
        session.revoked_at = now
        session.updated_at = now

        await self._repository.update(session)

    async def revoke_session_for_user(
        self,
        session_id: str,
        user_id: str,
    ) -> None:
        session = await self.get_by_id(session_id)

        if not session:
            raise SessionNotFoundError()

        if session.user_id != user_id:
            raise SessionAccessDeniedError()

        if not session.is_active:
            return

        await self.revoke(session)

    async def validate_refresh_token(
        self,
        refresh_token: str,
    ) -> Session:
        session = await self.get_by_refresh_token(
            refresh_token,
        )

        if not session:
            raise InvalidRefreshTokenError()

        if not session.is_active:
            raise SessionRevokedError()

        if session.expires_at <= datetime.now(timezone.utc):
            raise SessionExpiredError()

        return session

    async def revoke_all_sessions(
        self,
        user_id: str,
    ) -> None:
        sessions = await self._repository.get_active_user_sessions(
            user_id,
        )

        for session in sessions:
            await self.revoke(session)

    async def validate_session(
        self,
        session_id: str,
    ) -> Session:
        session = await self.get_by_id(
            session_id,
        )

        if not session:
            raise SessionNotFoundError()

        if not session.is_active:
            raise SessionRevokedError()

        if session.expires_at <= datetime.now(timezone.utc):
            raise SessionExpiredError()

        return session
