# app/two_factor/repository/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.two_factor.models import TwoFactorChallenge, UserSecuritySettings
from app.two_factor.repository.repository_interface import TwoFactorRepositoryInterface


class TwoFactorRepository(TwoFactorRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_settings(
        self,
        user_id: str,
        provider: str,
    ) -> UserSecuritySettings | None:
        result = await self._session.execute(
            select(UserSecuritySettings).where(
                UserSecuritySettings.user_id == user_id,
                UserSecuritySettings.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create_settings(
        self,
        user_id: str,
        provider: str,
    ) -> UserSecuritySettings:
        settings = await self.get_settings(user_id, provider)
        if settings:
            return settings

        settings = UserSecuritySettings(
            user_id=user_id,
            provider=provider,
        )
        self._session.add(settings)
        await self._session.flush()
        await self._session.refresh(settings)
        return settings

    async def update_settings(
        self,
        settings: UserSecuritySettings,
    ) -> UserSecuritySettings:
        self._session.add(settings)
        await self._session.commit()
        await self._session.refresh(settings)
        return settings

    async def create_challenge(
        self,
        challenge: TwoFactorChallenge,
    ) -> TwoFactorChallenge:
        self._session.add(challenge)
        await self._session.commit()
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
        provider: str,
    ) -> None:
        result = await self._session.execute(
            select(TwoFactorChallenge).where(
                TwoFactorChallenge.user_id == user_id,
                TwoFactorChallenge.purpose == purpose,
                TwoFactorChallenge.provider == provider,
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
        await self._session.commit()
        await self._session.refresh(challenge)
        return challenge
