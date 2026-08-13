# app/google_auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_auth_session_service
from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.db.session import get_session
from app.google_auth.repository import GoogleAuthRepository
from app.google_auth.repository_interface import GoogleAuthRepositoryInterface
from app.google_auth.service import GoogleAuthService
from app.google_auth.service_interface import GoogleAuthServiceInterface
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
    auth_session_service: Annotated[
        AuthSessionServiceInterface,
        Depends(get_auth_session_service),
    ],
) -> GoogleAuthServiceInterface:
    return GoogleAuthService(
        repository,
        user_repository,
        auth_session_service,
    )
