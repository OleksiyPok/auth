# app/users/dependencies.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.users.repository.repository import UserRepository
from app.users.repository.repository_interface import UserRepositoryInterface
from app.users.services.service import UserService
from app.users.services.service_interface import UserServiceInterface


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepositoryInterface:
    return UserRepository(session)


async def get_user_service(
    repository: UserRepositoryInterface = Depends(get_user_repository),
) -> UserServiceInterface:
    return UserService(repository)
