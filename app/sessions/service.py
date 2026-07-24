# app/sessions/service.py

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.sessions.interfaces import SessionRepositoryInterface
from app.sessions.models import Session


class SessionService:

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
            refresh_token_hash=self._hash_token(refresh_token),
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
        token_hash = self._hash_token(refresh_token)

        return await self._repository.get_by_refresh_token_hash(token_hash)

    async def validate_refresh_token(
        self,
        refresh_token: str,
    ) -> Session | None:
        session = await self.get_by_refresh_token(refresh_token)

        if not session:
            return None

        if not session.is_active:
            return None

        if session.expires_at <= datetime.now(timezone.utc):
            return None

        return session

    async def rotate_refresh_token(
        self,
        session: Session,
        new_refresh_token: str,
        expires_delta: timedelta,
    ) -> Session:
        now = datetime.now(timezone.utc)

        session.refresh_token_hash = self._hash_token(new_refresh_token)
        session.last_used_at = now
        session.updated_at = now
        session.expires_at = now + expires_delta

        return await self._repository.update(session)

    async def revoke(
        self,
        session: Session,
    ) -> None:
        now = datetime.now(timezone.utc)

        session.is_active = False
        session.revoked_at = now
        session.updated_at = now

        await self._repository.update(session)

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(64)

    @staticmethod
    def _hash_token(
        token: str,
    ) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def deactivate_user_sessions(
        self,
        user_id: str,
    ) -> None:
        await self._repository.deactivate_user_sessions(user_id)

    async def get_active_user_sessions(
        self,
        user_id: str,
    ) -> list[Session]:
        return await self._repository.get_active_user_sessions(user_id)
