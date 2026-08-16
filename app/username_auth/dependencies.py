# app/username_auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_auth_session_service
from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.db.session import get_session
from app.username_auth.repository.repository import UsernameIdentityRepository
from app.username_auth.repository.repository_interface import (
    UsernameIdentityRepositoryInterface,
)
from app.username_auth.services.login_service import UsernameLoginService
from app.username_auth.services.login_service_interface import UsernameLoginServiceInterface
from app.username_auth.services.register_service import UsernameRegisterService
from app.username_auth.services.register_service_interface import (
    UsernameRegisterServiceInterface,
)
from app.users.dependencies import get_user_repository
from app.users.repository.repository_interface import UserRepositoryInterface


async def get_local_identity_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> UsernameIdentityRepositoryInterface:
    return UsernameIdentityRepository(session)


async def get_local_register_service(
    user_repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    local_identity_repository: Annotated[
        UsernameIdentityRepositoryInterface,
        Depends(get_local_identity_repository),
    ],
) -> UsernameRegisterServiceInterface:
    return UsernameRegisterService(
        user_repository,
        local_identity_repository,
    )


async def get_local_login_service(
    local_identity_repository: Annotated[
        UsernameIdentityRepositoryInterface,
        Depends(get_local_identity_repository),
    ],
    user_repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    auth_session_service: Annotated[
        AuthSessionServiceInterface,
        Depends(get_auth_session_service),
    ],
) -> UsernameLoginServiceInterface:
    return UsernameLoginService(
        local_identity_repository,
        user_repository,
        auth_session_service,
    )
