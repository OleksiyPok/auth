# app/google_auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.google_auth.repository import GoogleAuthRepository
from app.google_auth.repository_interface import GoogleAuthRepositoryInterface
from app.google_auth.service import GoogleAuthService
from app.google_auth.service_interface import GoogleAuthServiceInterface
from app.sessions.dependencies import get_sessions_service
from app.sessions.services.service_interface import SessionServiceInterface
from app.users.dependencies import get_user_repository
from app.users.repository.repository_interface import UserRepositoryInterface


async def get_google_auth_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> GoogleAuthRepositoryInterface:
    return GoogleAuthRepository(session)


async def get_google_auth_service(
    repository: Annotated[
        GoogleAuthRepositoryInterface,
        Depends(get_google_auth_repository),
    ],
    user_repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    session_service: Annotated[
        SessionServiceInterface,
        Depends(get_sessions_service),
    ],
) -> GoogleAuthServiceInterface:
    return GoogleAuthService(
        repository,
        user_repository,
        session_service,
    )
