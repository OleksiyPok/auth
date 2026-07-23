# app/sessions/repository.py

from datetime import datetime
from typing import cast

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.sessions.interfaces import SessionRepositoryInterface
from app.sessions.models import Session


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
        await self._session.commit()
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
        await self._session.commit()
        await self._session.refresh(session)
        return session

    async def delete(
        self,
        session: Session,
    ) -> None:
        await self._session.delete(session)
        await self._session.commit()
