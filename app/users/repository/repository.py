# app/users/repository/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.auth.rbac.roles import Role
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface
from app.users.status import UserStatus


class UserRepository(UserRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(
        self,
        user_id: str,
    ) -> User | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        result = await self._session.execute(select(User))
        return list(result.scalars().all())

    async def create(
        self,
        user: User,
    ) -> User:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update(
        self,
        user: User,
    ) -> User:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def deactivate(self, user: User, status: UserStatus) -> User:
        user.status = status
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def delete(
        self,
        user: User,
    ) -> User:
        await self._session.delete(user)
        await self._session.flush()
        return user

    async def count_active_superadmins(self) -> int:
        stmt = select(func.count()).where(
            User.role == Role.SUPERADMIN,
            User.status == UserStatus.ACTIVE,
        )

        result = await self._session.execute(stmt)

        return result.scalar_one()
