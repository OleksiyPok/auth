# app/google/dependencies.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.google.repository import GoogleRepository
from app.google.repository_interface import GoogleRepositoryInterface
from app.google.service import GoogleService
from app.google.service_interface import GoogleServiceInterface


async def get_google_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> GoogleRepositoryInterface:
    return GoogleRepository(session)


async def get_google_service(
    repository: Annotated[
        GoogleRepositoryInterface,
        Depends(get_google_repository),
    ],
) -> GoogleServiceInterface:
    return GoogleService(repository)
