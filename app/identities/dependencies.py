# app/identities/dependencies.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.email_auth.repository.repository import EmailIdentityRepository
from app.google_auth.repository.repository import GoogleAuthRepository
from app.identities.services.service import IdentityService
from app.identities.services.service_interface import IdentityServiceInterface
from app.sessions.repository.repository import SessionRepository
from app.username_auth.repository.repository import UsernameIdentityRepository
from app.users.repository.repository import UserRepository


async def get_identity_service(
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> IdentityServiceInterface:
    return IdentityService(
        EmailIdentityRepository(session),
        UsernameIdentityRepository(session),
        GoogleAuthRepository(session),
        UserRepository(session),
        SessionRepository(session),
    )
