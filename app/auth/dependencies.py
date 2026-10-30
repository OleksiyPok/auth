# app/auth/dependencies.py

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)

from app.auth.exceptions import FreshSessionRequiredError, InvalidAccessTokenError
from app.auth.services.auth_session_service import AuthSessionService
from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.auth.services.token_service import TokenService
from app.auth.services.token_service_interface import TokenServiceInterface
from app.core.config import settings
from app.identities.dependencies import get_identity_service
from app.identities.services.service_interface import IdentityServiceInterface
from app.infrastructure.jwt.security import decode_access_token
from app.sessions.dependencies import get_sessions_service
from app.sessions.schemas import CurrentSessionSchema
from app.sessions.services.service_interface import SessionServiceInterface
from app.users.dependencies import get_user_repository
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface

username_auth_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/username/login",
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
    identity_service: Annotated[
        IdentityServiceInterface,
        Depends(get_identity_service),
    ],
) -> TokenServiceInterface:
    return TokenService(
        repository,
        session_service,
        auth_session_service,
        identity_service,
    )


async def get_access_token(
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
) -> str:
    # All three schemes read the same "Authorization: Bearer ..." header.
    # They are listed so that Swagger sends the token after authorizing
    # with any of them.
    token = credentials.credentials if credentials else username_token or email_token

    if token is None:
        raise InvalidAccessTokenError()
    return token


async def get_current_user(
    token: Annotated[
        str,
        Depends(get_access_token),
    ],
    authentication_service: Annotated[
        TokenServiceInterface,
        Depends(get_token_service),
    ],
) -> User:
    return await authentication_service.authenticate(token)


async def get_current_session(
    # Listed first: the token is fully validated (signature, session,
    # identity ownership, active user) before its claims are read below.
    _current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    token: Annotated[
        str,
        Depends(get_access_token),
    ],
) -> CurrentSessionSchema:
    payload = decode_access_token(token)

    return CurrentSessionSchema(
        session_id=payload["sid"],
        identity_id=payload["identity_id"],
    )


async def require_fresh_session(
    current_session: Annotated[
        CurrentSessionSchema,
        Depends(get_current_session),
    ],
    session_service: Annotated[
        SessionServiceInterface,
        Depends(get_sessions_service),
    ],
) -> None:
    """Refuse a session that was created longer ago than the fresh window.

    A refresh keeps the creation time, so only a new sign-in makes it fresh.
    """
    session = await session_service.validate_session(current_session.session_id)

    age = datetime.now(timezone.utc) - session.created_at

    if age > timedelta(minutes=settings.FRESH_SESSION_MINUTES):
        raise FreshSessionRequiredError()


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
