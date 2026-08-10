# app/local_auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.local_auth.login_service import LocalLoginService
from app.local_auth.login_service_interface import LocalLoginServiceInterface
from app.local_auth.register_service import LocalRegisterService
from app.local_auth.register_service_interface import LocalRegisterServiceInterface
from app.local_auth.repository import LocalIdentityRepository
from app.local_auth.repository_interface import LocalIdentityRepositoryInterface
from app.local_auth.service import LocalAuthService
from app.local_auth.service_interface import LocalAuthServiceInterface
from app.sessions.dependencies import get_sessions_service
from app.sessions.service_interface import SessionServiceInterface
from app.users.dependencies import get_user_repository
from app.users.repository_interface import UserRepositoryInterface


async def get_local_identity_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> LocalIdentityRepositoryInterface:
    return LocalIdentityRepository(session)


async def get_local_auth_service(
    repository: Annotated[
        LocalIdentityRepositoryInterface,
        Depends(get_local_identity_repository),
    ],
) -> LocalAuthServiceInterface:
    return LocalAuthService(repository)


async def get_local_register_service(
    user_repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    local_identity_repository: Annotated[
        LocalIdentityRepositoryInterface,
        Depends(get_local_identity_repository),
    ],
) -> LocalRegisterServiceInterface:
    return LocalRegisterService(
        user_repository,
        local_identity_repository,
    )


async def get_local_login_service(
    local_auth_service: Annotated[
        LocalAuthServiceInterface,
        Depends(get_local_auth_service),
    ],
    user_repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    session_service: Annotated[
        SessionServiceInterface,
        Depends(get_sessions_service),
    ],
) -> LocalLoginServiceInterface:
    return LocalLoginService(
        local_auth_service,
        user_repository,
        session_service,
    )
