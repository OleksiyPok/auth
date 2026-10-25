# app/two_factor/repository/repository.py

from datetime import datetime, timezone

from sqlalchemy import delete, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.db.session import session_factory
from app.two_factor.models import (
    TwoFactorChallenge,
    TwoFactorMethod,
    UserSecuritySettings,
)
from app.two_factor.repository.repository_interface import TwoFactorRepositoryInterface


class TwoFactorRepository(TwoFactorRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_settings(self, user_id: str) -> UserSecuritySettings | None:
        result = await self._session.execute(
            select(UserSecuritySettings).where(
                UserSecuritySettings.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create_settings(
        self,
        user_id: str,
    ) -> UserSecuritySettings:
        settings = await self.get_settings(user_id)
        if settings:
            return settings

        settings = UserSecuritySettings(user_id=user_id)
        self._session.add(settings)
        await self._session.flush()
        await self._session.refresh(settings)
        return settings

    async def update_settings(
        self,
        settings: UserSecuritySettings,
    ) -> UserSecuritySettings:
        self._session.add(settings)
        await self._session.flush()
        await self._session.refresh(settings)
        return settings

    async def create_challenge(
        self,
        challenge: TwoFactorChallenge,
    ) -> TwoFactorChallenge:
        self._session.add(challenge)
        await self._session.flush()
        await self._session.refresh(challenge)
        return challenge

    async def get_challenge(
        self,
        challenge_id: str,
    ) -> TwoFactorChallenge | None:
        result = await self._session.execute(
            select(TwoFactorChallenge).where(TwoFactorChallenge.id == challenge_id)
        )
        return result.scalar_one_or_none()

    async def invalidate_active_challenges(
        self,
        user_id: str,
        purpose: str,
    ) -> None:
        result = await self._session.execute(
            select(TwoFactorChallenge).where(
                TwoFactorChallenge.user_id == user_id,
                TwoFactorChallenge.purpose == purpose,
                TwoFactorChallenge.used == False,
            )
        )
        for challenge in result.scalars().all():
            challenge.used = True

        await self._session.flush()

    async def update_challenge(
        self,
        challenge: TwoFactorChallenge,
    ) -> TwoFactorChallenge:
        self._session.add(challenge)
        await self._session.flush()
        await self._session.refresh(challenge)
        return challenge

    # noinspection PyMethodMayBeStatic
    async def increment_challenge_attempts(self, challenge_id: str) -> int:
        # Separate transaction: the counter must survive the rollback of the
        # request transaction that happens when the service raises an error.
        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    update(TwoFactorChallenge)
                    .where(col(TwoFactorChallenge.id) == challenge_id)
                    .values(attempts=TwoFactorChallenge.attempts + 1)
                )
                result = await session.execute(
                    select(TwoFactorChallenge.attempts).where(
                        TwoFactorChallenge.id == challenge_id
                    )
                )
                return result.scalar_one()

    async def create_method(self, method: TwoFactorMethod) -> TwoFactorMethod:
        self._session.add(method)
        await self._session.flush()
        await self._session.refresh(method)
        return method

    async def list_methods(self, user_id: str) -> list[TwoFactorMethod]:
        result = await self._session.execute(
            select(TwoFactorMethod)
            .where(TwoFactorMethod.user_id == user_id)
            .order_by(col(TwoFactorMethod.created_at))
        )
        return list(result.scalars().all())

    async def get_method(
        self,
        user_id: str,
        method_id: str,
    ) -> TwoFactorMethod | None:
        result = await self._session.execute(
            select(TwoFactorMethod).where(
                TwoFactorMethod.user_id == user_id,
                TwoFactorMethod.id == method_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_method(self, method: TwoFactorMethod) -> TwoFactorMethod:
        self._session.add(method)
        await self._session.flush()
        await self._session.refresh(method)
        return method

    async def delete_challenges_by_method_id(self, method_id: str) -> None:
        await self._session.execute(
            delete(TwoFactorChallenge).where(
                col(TwoFactorChallenge.method_id) == method_id
            )
        )

    async def delete_method(self, method: TwoFactorMethod) -> None:
        await self._session.delete(method)
        await self._session.flush()

    async def delete_expired_or_used_challenges(self) -> None:
        await self._session.execute(
            delete(TwoFactorChallenge).where(
                or_(
                    col(TwoFactorChallenge.used).is_(True),
                    col(TwoFactorChallenge.expires_at) <= datetime.now(timezone.utc),
                )
            )
        )

    async def delete_by_user_id(self, user_id: str) -> None:
        await self._session.execute(
            delete(TwoFactorChallenge).where(col(TwoFactorChallenge.user_id) == user_id)
        )
        await self._session.execute(
            delete(TwoFactorMethod).where(col(TwoFactorMethod.user_id) == user_id)
        )
        await self._session.execute(
            delete(UserSecuritySettings).where(
                col(UserSecuritySettings.user_id) == user_id
            )
        )
