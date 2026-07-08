# app/users/dependencies.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.users.interfaces import UserRepositoryInterface
from app.users.repository import UserRepository


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepositoryInterface:
    return UserRepository(session)
