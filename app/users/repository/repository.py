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

    async def get_for_update(self, user_id: str) -> User | None:
        # FOR UPDATE locks the row until the transaction ends on PostgreSQL;
        # SQLite ignores it.
        result = await self._session.execute(
            select(User).where(User.id == user_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_pair_for_update(
        self, first_user_id: str, second_user_id: str
    ) -> tuple[User | None, User | None]:
        """Lock two users in the order of their ids and return them as requested.

        The same pair is always locked in the same order, so two transactions
        working on the same two users cannot block each other forever.
        """
        low_id, high_id = sorted((first_user_id, second_user_id))

        low = await self.get_for_update(low_id)
        high = low if high_id == low_id else await self.get_for_update(high_id)

        users = {low_id: low, high_id: high}
        return users[first_user_id], users[second_user_id]
