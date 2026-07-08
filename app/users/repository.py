# app/users/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.users.interfaces import UserRepositoryInterface
from app.users.models import User


class UserRepository(UserRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        self._session.add(user)

        await self._session.commit()
        await self._session.refresh(user)

        return user

    async def get_by_id(
        self,
        user_id: str,
    ) -> User | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_login(
        self,
        login: str,
    ) -> User | None:
        result = await self._session.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()
