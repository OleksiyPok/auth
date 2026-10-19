# app/email_auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.email_auth.repository.repository import EmailIdentityRepository
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.email_auth.services.login_service import EmailLoginService
from app.email_auth.services.login_service_interface import EmailLoginServiceInterface
from app.email_auth.services.register_service import EmailRegisterService
from app.email_auth.services.register_service_interface import (
    EmailRegisterServiceInterface,
)
from app.infrastructure.email.base import EmailService
from app.two_factor.dependencies import get_email_service, get_two_factor_service
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.users.dependencies import get_user_repository
from app.users.repository.repository_interface import UserRepositoryInterface


async def get_email_identity_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EmailIdentityRepositoryInterface:
    return EmailIdentityRepository(session)


async def get_email_register_service(
    user_repository: Annotated[UserRepositoryInterface, Depends(get_user_repository)],
    email_identity_repository: Annotated[
        EmailIdentityRepositoryInterface, Depends(get_email_identity_repository)
    ],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> EmailRegisterServiceInterface:
    return EmailRegisterService(
        user_repository,
        email_identity_repository,
        email_service,
    )


async def get_email_login_service(
    email_identity_repository: Annotated[
        EmailIdentityRepositoryInterface, Depends(get_email_identity_repository)
    ],
    user_repository: Annotated[UserRepositoryInterface, Depends(get_user_repository)],
    two_factor_service: Annotated[
        TwoFactorServiceInterface, Depends(get_two_factor_service)
    ],
) -> EmailLoginServiceInterface:
    return EmailLoginService(
        email_identity_repository,
        user_repository,
        two_factor_service,
    )
