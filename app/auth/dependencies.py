# app/auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.services.login_service import LoginService
from app.auth.services.register_service import RegisterService
from app.auth.services.token_service import TokenService
from app.sessions.dependencies import get_sessions_service
from app.sessions.service import SessionService
from app.users.dependencies import get_user_repository
from app.users.models import User
from app.users.repository_interface import UserRepositoryInterface

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_register_service(
    repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
) -> RegisterService:
    return RegisterService(repository)


def get_login_service(
    repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    session_service: Annotated[
        SessionService,
        Depends(get_sessions_service),
    ],
) -> LoginService:
    return LoginService(
        repository,
        session_service,
    )


def get_token_service(
    repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    session_service: Annotated[
        SessionService,
        Depends(get_sessions_service),
    ],
) -> TokenService:
    return TokenService(
        repository,
        session_service,
    )


async def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    authentication_service: Annotated[
        TokenService,
        Depends(get_token_service),
    ],
) -> User:
    return await authentication_service.authenticate(token)
