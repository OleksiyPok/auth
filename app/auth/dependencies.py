# app/auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.services.token_service import TokenService
from app.auth.services.token_service_interface import TokenServiceInterface
from app.sessions.dependencies import get_sessions_service
from app.sessions.services.service_interface import SessionServiceInterface
from app.users.dependencies import get_user_repository
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_token_service(
    repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    session_service: Annotated[
        SessionServiceInterface,
        Depends(get_sessions_service),
    ],
) -> TokenServiceInterface:
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
        TokenServiceInterface,
        Depends(get_token_service),
    ],
) -> User:
    return await authentication_service.authenticate(token)
