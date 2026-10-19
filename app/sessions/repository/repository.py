# app/sessions/repository/repository.py

from datetime import datetime, timezone
from typing import cast

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.sessions.models import Session
from app.sessions.repository.repository_interface import SessionRepositoryInterface


class SessionRepository(SessionRepositoryInterface):

    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def create(
        self,
        session: Session,
    ) -> Session:
        self._session.add(session)
        await self._session.flush()
        await self._session.refresh(session)
        return session

    async def get_by_id(
        self,
        session_id: str,
    ) -> Session | None:
        statement = select(Session).where(
            cast(ColumnElement[str], Session.id) == session_id
        )

        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_refresh_token_hash(
        self,
        refresh_token_hash: str,
    ) -> Session | None:
        statement = select(Session).where(
            cast(
                ColumnElement[str],
                Session.refresh_token_hash,
            )
            == refresh_token_hash
        )

        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_sessions(
        self,
        user_id: str,
    ) -> list[Session]:
        statement = (
            select(Session)
            .where(
                cast(
                    ColumnElement[str],
                    Session.user_id,
                )
                == user_id
            )
            .order_by(
                desc(
                    cast(
                        ColumnElement[datetime],
                        Session.created_at,
                    )
                )
            )
        )

        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def update(
        self,
        session: Session,
    ) -> Session:
        self._session.add(session)
        await self._session.flush()
        await self._session.refresh(session)
        return session

    async def delete(
        self,
        session: Session,
    ) -> None:
        await self._session.delete(session)
        await self._session.flush()

    async def get_active_user_sessions(
        self,
        user_id: str,
    ) -> list[Session]:
        statement = (
            select(Session)
            .where(
                cast(
                    ColumnElement[str],
                    Session.user_id,
                )
                == user_id
            )
            .where(
                cast(
                    ColumnElement[bool],
                    Session.is_active,
                )
            )
            .order_by(
                desc(
                    cast(
                        ColumnElement[datetime],
                        Session.created_at,
                    )
                )
            )
        )

        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def get_active_identity_sessions(
        self,
        identity_id: str,
    ) -> list[Session]:
        statement = (
            select(Session)
            .where(
                cast(
                    ColumnElement[str],
                    Session.identity_id,
                )
                == identity_id
            )
            .where(
                cast(
                    ColumnElement[bool],
                    Session.is_active,
                )
            )
            .order_by(
                desc(
                    cast(
                        ColumnElement[datetime],
                        Session.created_at,
                    )
                )
            )
        )

        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def deactivate_user_sessions(
        self,
        user_id: str,
    ) -> None:
        statement = (
            update(Session)
            .where(
                cast(
                    ColumnElement[str],
                    Session.user_id,
                )
                == user_id
            )
            .where(
                cast(
                    ColumnElement[bool],
                    Session.is_active,
                )
            )
            .values(
                is_active=False,
                revoked_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )

        await self._session.execute(statement)
        await self._session.flush()

    async def deactivate_identity_sessions(
        self,
        identity_id: str,
    ) -> None:
        now = datetime.now(timezone.utc)

        statement = (
            update(Session)
            .where(
                cast(
                    ColumnElement[str],
                    Session.identity_id,
                )
                == identity_id
            )
            .where(
                cast(
                    ColumnElement[bool],
                    Session.is_active,
                )
            )
            .values(
                is_active=False,
                revoked_at=now,
                updated_at=now,
            )
        )

        await self._session.execute(statement)
        await self._session.flush()
