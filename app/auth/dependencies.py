# app/auth/dependencies.py

from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)

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

username_auth_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="Username Authentication",
    auto_error=False,
)

email_auth_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/email/login",
    scheme_name="Email Authentication",
    auto_error=False,
)

generic_auth_scheme = HTTPBearer(
    scheme_name="Authentication",
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
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(generic_auth_scheme),
    ],
    username_token: Annotated[
        str | None,
        Depends(username_auth_scheme),
    ],
    email_token: Annotated[
        str | None,
        Depends(email_auth_scheme),
    ],
    authentication_service: Annotated[
        TokenServiceInterface,
        Depends(get_token_service),
    ],
) -> User:
    # All three schemes read the same "Authorization: Bearer ..." header.
    # They are listed so that Swagger sends the token after authorizing
    # with any of them.
    token = credentials.credentials if credentials else username_token or email_token

    if token is None:
        raise InvalidAccessTokenError()
    return await authentication_service.authenticate(token)


async def get_current_username_user(
    credentials: Annotated[
        str | None,
        Depends(username_auth_scheme),
    ],
    authentication_service: Annotated[
        TokenServiceInterface,
        Depends(get_token_service),
    ],
) -> User:
    if credentials is None:
        raise InvalidAccessTokenError()
    return await authentication_service.authenticate(credentials)


async def get_current_email_user(
    credentials: Annotated[
        str | None,
        Depends(email_auth_scheme),
    ],
    authentication_service: Annotated[
        TokenServiceInterface,
        Depends(get_token_service),
    ],
) -> User:
    if credentials is None:
        raise InvalidAccessTokenError()
    return await authentication_service.authenticate(credentials)


async def get_current_google_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(google_auth_scheme),
    ],
    authentication_service: Annotated[
        TokenServiceInterface,
        Depends(get_token_service),
    ],
) -> User:
    if credentials is None:
        raise InvalidAccessTokenError()
    return await authentication_service.authenticate(
        credentials.credentials,
    )
