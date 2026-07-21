# app/users/dependencies.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.users.interfaces import UserRepositoryInterface
from app.users.models import User
from app.users.repository import UserRepository
from app.users.service import UserService


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepositoryInterface:
    return UserRepository(session)


async def get_user_service(
    repository: UserRepositoryInterface = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)


# async def get_current_user(
#
#     return user
