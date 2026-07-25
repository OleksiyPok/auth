# app/auth/dependencies.py

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.exceptions import InsufficientPermissionsError
from app.auth.service import AuthService
from app.sessions.dependencies import get_sessions_service
from app.sessions.interfaces import SessionServiceInterface
from app.users.dependencies import get_user_repository
from app.users.enums import UserRole
from app.users.interfaces import UserRepositoryInterface
from app.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_ADMIN_ROLES = frozenset({UserRole.ADMIN, UserRole.SUPERADMIN})


def _user_has_any_role(user: User, allowed_roles: frozenset[UserRole]) -> bool:
    try:
        role = UserRole(user.role)
    except ValueError:
        return False
    return role in allowed_roles


def get_auth_service(
    repository: Annotated[
        UserRepositoryInterface,
        Depends(get_user_repository),
    ],
    session_service: Annotated[
        SessionServiceInterface,
        Depends(get_sessions_service),
    ],
) -> AuthService:
    return AuthService(
        repository,
        session_service,
    )


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


def require_role(
    *allowed_roles: UserRole,
) -> Callable[..., User]:
    roles = frozenset(allowed_roles)

    async def checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not _user_has_any_role(current_user, roles):
            raise InsufficientPermissionsError()
        return current_user

    return checker


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not _user_has_any_role(current_user, _ADMIN_ROLES):
        raise InsufficientPermissionsError()
    return current_user
