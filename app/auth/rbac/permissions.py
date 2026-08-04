# app/auth/rbac/permissions.py

"""
Centralized authorization dependencies for RBAC.

This module provides FastAPI dependencies for permission-based access control.
All authorization logic is centralized here - no ad-hoc role checks in routers.
"""

from typing import Awaitable, Callable

from fastapi import Depends, HTTPException, status

from app.auth.exceptions import InsufficientPermissionsError
from app.auth.rbac.rbac import Permission, get_permissions_for_role, is_valid_role
from app.users.models import User

# Type alias for user getter function
UserGetter = Callable[..., Awaitable[User]]


def get_user_permissions(user: User) -> set[str]:
    """Get all permissions for a user based on their role."""
    if not is_valid_role(user.role):
        # Invalid role - no permissions
        return set()
    return get_permissions_for_role(user.role)


def _resolve_user_getter(user_getter: UserGetter | None) -> UserGetter:
    if user_getter is not None:
        return user_getter

    from app.auth.dependencies import get_current_user

    return get_current_user


def _create_permission_dependency(
    required_permissions: set[str],
    user_getter: UserGetter,
    require_all: bool = True,
):
    """
    Internal factory for creating permission dependencies.

    Args:
        required_permissions: Set of required permission strings
        user_getter: Async function that returns the current user
        require_all: If True, all permissions required (AND). If False, any permission (OR).
    """
    # Validate permissions at startup
    for perm in required_permissions:
        if not Permission.validate(perm):
            raise ValueError(f"Invalid permission: '{perm}'")

    async def _check_permissions(current_user: User = Depends(user_getter)) -> User:
        user_permissions = get_user_permissions(current_user)

        if require_all:
            if not required_permissions.issubset(user_permissions):
                raise InsufficientPermissionsError()
        else:
            if not required_permissions.intersection(user_permissions):
                raise InsufficientPermissionsError()

        return current_user

    return _check_permissions


def require_permissions(
    *required_permissions: str, user_getter: UserGetter | None = None
):
    """
    Dependency factory that requires specific permissions (ALL must be present).

    Usage:
        @router.get("/admin", dependencies=[Depends(require_permissions(Permission.ADMIN_ACCESS))])
        async def admin_only(...):
            ...

    Or with multiple permissions (ALL must be present):
        @router.post("/users", dependencies=[Depends(require_permissions(Permission.USERS_WRITE, Permission.USERS_READ))])
        async def create_user(...):
            ...

    For testing, pass a custom user_getter:
        require_permissions(Permission.USERS_READ, user_getter=mock_user_getter)
    """
    getter = _resolve_user_getter(user_getter)
    required = set(required_permissions)
    return _create_permission_dependency(required, getter, require_all=True)


def require_any_permission(
    *required_permissions: str, user_getter: UserGetter | None = None
):
    """
    Dependency factory that requires at least one of the specified permissions.

    Usage:
        @router.get("/reports", dependencies=[Depends(require_any_permission(Permission.ADMIN_VIEW_LOGS, Permission.USERS_READ))])
        async def view_reports(...):
            ...
    """
    getter = _resolve_user_getter(user_getter)
    required = set(required_permissions)
    return _create_permission_dependency(required, getter, require_all=False)


def require_role(*allowed_roles: str, user_getter: UserGetter | None = None):
    """
    Dependency factory that requires a specific role.

    Note: Prefer `require_permissions` for most cases. Use this only when
    you genuinely need role-based access (e.g., role management endpoints).

    Usage:
        @router.post("/roles", dependencies=[Depends(require_role("superadmin"))])
        async def create_role(...):
            ...
    """
    getter = _resolve_user_getter(user_getter)
    allowed = set(allowed_roles)

    # Validate roles at startup
    for role in allowed:
        if not is_valid_role(role):
            raise ValueError(f"Invalid role: '{role}'")

    async def _check_role(
        current_user: User = Depends(getter),
    ) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_ROLE",
                    "message": "Insufficient role to perform this action",
                    "required_roles": sorted(allowed),
                    "user_role": current_user.role,
                },
            )
        return current_user

    return _check_role


# Convenience dependencies for common permission sets


def require_admin_access(user_getter: UserGetter | None = None):
    """Require ADMIN_ACCESS permission."""
    return require_permissions(Permission.ADMIN_ACCESS, user_getter=user_getter)


def require_user_management(user_getter: UserGetter | None = None):
    """Require ADMIN_MANAGE_USERS permission."""
    return require_permissions(Permission.ADMIN_MANAGE_USERS, user_getter=user_getter)


def require_role_management(user_getter: UserGetter | None = None):
    """Require ADMIN_MANAGE_ROLES permission."""
    return require_permissions(Permission.ADMIN_MANAGE_ROLES, user_getter=user_getter)


def require_users_read(user_getter: UserGetter | None = None):
    """Require USERS_READ permission."""
    return require_permissions(Permission.USERS_READ, user_getter=user_getter)


def require_users_write(user_getter: UserGetter | None = None):
    """Require USERS_WRITE permission."""
    return require_permissions(Permission.USERS_WRITE, user_getter=user_getter)


def require_users_delete(user_getter: UserGetter | None = None):
    """Require USERS_DELETE permission."""
    return require_permissions(Permission.USERS_DELETE, user_getter=user_getter)


def require_users_list(user_getter: UserGetter | None = None):
    """Require USERS_LIST permission."""
    return require_permissions(Permission.USERS_LIST, user_getter=user_getter)


def require_sessions_read(user_getter: UserGetter | None = None):
    """Require SESSIONS_READ permission."""
    return require_permissions(Permission.SESSIONS_READ, user_getter=user_getter)


def require_sessions_revoke(user_getter: UserGetter | None = None):
    """Require SESSIONS_REVOKE permission."""
    return require_permissions(Permission.SESSIONS_REVOKE, user_getter=user_getter)


def require_sessions_revoke_all(user_getter: UserGetter | None = None):
    """Require SESSIONS_REVOKE_ALL permission."""
    return require_permissions(Permission.SESSIONS_REVOKE_ALL, user_getter=user_getter)


def require_self_read(user_getter: UserGetter | None = None):
    """Require SELF_READ permission."""
    return require_permissions(Permission.SELF_READ, user_getter=user_getter)


def require_self_write(user_getter: UserGetter | None = None):
    """Require SELF_WRITE permission."""
    return require_permissions(Permission.SELF_WRITE, user_getter=user_getter)


def require_self_delete(user_getter: UserGetter | None = None):
    """Require SELF_DELETE permission."""
    return require_permissions(Permission.SELF_DELETE, user_getter=user_getter)


def require_self_sessions_read(user_getter: UserGetter | None = None):
    """Require SELF_SESSIONS_READ permission."""
    return require_permissions(Permission.SELF_SESSIONS_READ, user_getter=user_getter)


def require_self_sessions_revoke(user_getter: UserGetter | None = None):
    """Require SELF_SESSIONS_REVOKE permission."""
    return require_permissions(Permission.SELF_SESSIONS_REVOKE, user_getter=user_getter)
