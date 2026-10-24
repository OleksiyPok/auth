# app/two_factor/dependencies.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_auth_session_service
from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.db.session import get_session
from app.email_auth.repository.repository import EmailIdentityRepository
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.infrastructure.email.base import EmailService
from app.infrastructure.email.manager import EmailManager
from app.two_factor.repository.repository import TwoFactorRepository
from app.two_factor.repository.repository_interface import TwoFactorRepositoryInterface
from app.two_factor.senders.email_sender import EmailTwoFactorSender
from app.two_factor.senders.sender_interface import TwoFactorSenderInterface
from app.two_factor.services.service import TwoFactorService
from app.two_factor.services.service_interface import TwoFactorServiceInterface


async def get_two_factor_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TwoFactorRepositoryInterface:
    return TwoFactorRepository(session)


async def get_email_identity_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EmailIdentityRepositoryInterface:
    return EmailIdentityRepository(session)


async def get_email_service() -> EmailService:
    return EmailManager()


async def get_two_factor_sender(
    email_service: Annotated[
        EmailService,
        Depends(get_email_service),
    ],
) -> TwoFactorSenderInterface:
    return EmailTwoFactorSender(email_service)


async def get_two_factor_service(
    repository: Annotated[
        TwoFactorRepositoryInterface,
        Depends(get_two_factor_repository),
    ],
    email_identity_repository: Annotated[
        EmailIdentityRepositoryInterface,
        Depends(get_email_identity_repository),
    ],
    auth_session_service: Annotated[
        AuthSessionServiceInterface,
        Depends(get_auth_session_service),
    ],
    email_service: Annotated[
        EmailService,
        Depends(get_email_service),
    ],
    sender: Annotated[
        TwoFactorSenderInterface,
        Depends(get_two_factor_sender),
    ],
) -> TwoFactorServiceInterface:
    return TwoFactorService(
        repository=repository,
        email_identity_repository=email_identity_repository,
        auth_session_service=auth_session_service,
        email_service=email_service,
        sender=sender,
    )
