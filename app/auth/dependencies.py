# app/auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.service import AuthService
from app.users.dependencies import get_user_repository
from app.users.interfaces import UserRepositoryInterface
from app.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(
    repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
) -> AuthService:
    return AuthService(repository)


async def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    auth_service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
) -> User:
    return await auth_service.authenticate_token(token)
