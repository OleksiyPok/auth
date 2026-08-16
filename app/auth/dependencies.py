# app/auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.exceptions import InvalidAccessTokenError
from app.auth.services.auth_session_service import AuthSessionService
from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.auth.services.token_service import TokenService
from app.auth.services.token_service_interface import TokenServiceInterface
from app.sessions.dependencies import get_sessions_service
from app.sessions.services.service_interface import SessionServiceInterface
from app.users.dependencies import get_user_repository
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface

local_auth_scheme = HTTPBearer(
    scheme_name="Local Authentication",
    auto_error=False,
)

email_auth_scheme = HTTPBearer(
    scheme_name="Email Authentication",
    auto_error=False,
)

google_auth_scheme = HTTPBearer(
    scheme_name="Google Authentication",
    auto_error=False,
)


def get_auth_session_service(
    session_service: Annotated[
        SessionServiceInterface,
        Depends(get_sessions_service),
    ],
) -> AuthSessionServiceInterface:
    return AuthSessionService(
        session_service,
    )


def get_token_service(
    repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    session_service: Annotated[
        SessionServiceInterface,
        Depends(get_sessions_service),
    ],
    auth_session_service: Annotated[
        AuthSessionServiceInterface,
        Depends(get_auth_session_service),
    ],
) -> TokenServiceInterface:
    return TokenService(
        repository,
        session_service,
        auth_session_service,
    )


async def get_current_user(
    local_credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(local_auth_scheme),
    ],
    email_credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(email_auth_scheme),
    ],
    google_credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(google_auth_scheme),
    ],
    authentication_service: Annotated[
        TokenServiceInterface,
        Depends(get_token_service),
    ],
) -> User:
    credentials = local_credentials or email_credentials or google_credentials

    if credentials is None:
        raise InvalidAccessTokenError()

    return await authentication_service.authenticate(
        credentials.credentials,
    )
