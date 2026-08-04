# app/auth/rbac.py

"""
Role-Based Access Control (RBAC) core module.

This module defines:
- Permissions: Stable, validated identifiers for fine-grained access control
- Roles: Named collections of permissions
- Role-to-Permission mapping: Declarative configuration

Design principles:
- Permissions are the atomic unit of authorization
- Roles grant permissions; users receive permissions through roles
- No hardcoded role checks in business logic (use permissions instead)
- Configuration-driven: add/change roles and permissions without code changes
- Permissions have stable, validated identifiers
"""

from enum import StrEnum
from typing import Final

from fastapi import HTTPException, status


class Permission(StrEnum):
    """
    Stable permission identifiers.

    Naming convention: RESOURCE_ACTION
    - RESOURCE: plural noun (users, sessions, roles, admin, self)
    - ACTION: read, write, delete, manage, revoke, access

    Use Permission.validate() to check if a string is a valid permission.
    """

    # Admin permissions
    ADMIN_ACCESS = "admin.access"
    ADMIN_MANAGE_USERS = "admin.manage_users"
    ADMIN_MANAGE_ROLES = "admin.manage_roles"
    ADMIN_VIEW_LOGS = "admin.view_logs"
    ADMIN_VIEW_METRICS = "admin.view_metrics"

    # User management permissions
    USERS_READ = "users.read"
    USERS_WRITE = "users.write"
    USERS_DELETE = "users.delete"
    USERS_LIST = "users.list"

    # Session management permissions
    SESSIONS_READ = "sessions.read"
    SESSIONS_REVOKE = "sessions.revoke"
    SESSIONS_REVOKE_ALL = "sessions.revoke_all"

    # Role management permissions
    ROLES_READ = "roles.read"
    ROLES_WRITE = "roles.write"
    ROLES_DELETE = "roles.delete"

    # Self permissions (for users acting on their own resources)
    SELF_READ = "self.read"
    SELF_WRITE = "self.write"
    SELF_DELETE = "self.delete"
    SELF_SESSIONS_READ = "self.sessions.read"
    SELF_SESSIONS_REVOKE = "self.sessions.revoke"

    @classmethod
    def validate(cls, value: str) -> bool:
        """Check if a string is a valid permission identifier."""
        return value in cls._value2member_map_

    @classmethod
    def all(cls) -> set[str]:
        """Return all defined permissions as a set."""
        return set(cls._value2member_map_.keys())


# Role definitions
# These are the built-in roles. In production, these could be loaded from config/database.
class Role(StrEnum):
    """Built-in role identifiers."""

    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

    @classmethod
    def validate(cls, value: str) -> bool:
        """Check if a string is a valid role identifier."""
        return value in cls._value2member_map_


# Default role assigned to new users
DEFAULT_ROLE: Final[str] = Role.USER


# Declarative role -> permissions mapping
# This is the single source of truth for what permissions each role has.
# Modify this mapping to change role permissions without touching authorization logic.
# Keys are string role identifiers (not Role enum) for easier config-driven usage.
ROLE_PERMISSIONS: Final[dict[str, set[str]]] = {
    Role.USER: {
        # Self permissions
        Permission.SELF_READ,
        Permission.SELF_WRITE,
        Permission.SELF_DELETE,
        Permission.SELF_SESSIONS_READ,
        Permission.SELF_SESSIONS_REVOKE,
    },
    Role.ADMIN: {
        # All user permissions
        Permission.SELF_READ,
        Permission.SELF_WRITE,
        Permission.SELF_DELETE,
        Permission.SELF_SESSIONS_READ,
        Permission.SELF_SESSIONS_REVOKE,
        # User management
        Permission.USERS_READ,
        Permission.USERS_WRITE,
        Permission.USERS_LIST,
        # Session management
        Permission.SESSIONS_READ,
        Permission.SESSIONS_REVOKE,
        # Admin access
        Permission.ADMIN_ACCESS,
        Permission.ADMIN_VIEW_LOGS,
        Permission.ADMIN_VIEW_METRICS,
    },
    Role.SUPERADMIN: {
        # All admin permissions
        Permission.SELF_READ,
        Permission.SELF_WRITE,
        Permission.SELF_DELETE,
        Permission.SELF_SESSIONS_READ,
        Permission.SELF_SESSIONS_REVOKE,
        Permission.USERS_READ,
        Permission.USERS_WRITE,
        Permission.USERS_DELETE,
        Permission.USERS_LIST,
        Permission.SESSIONS_READ,
        Permission.SESSIONS_REVOKE,
        Permission.SESSIONS_REVOKE_ALL,
        Permission.ADMIN_ACCESS,
        Permission.ADMIN_MANAGE_USERS,
        Permission.ADMIN_MANAGE_ROLES,
        Permission.ADMIN_VIEW_LOGS,
        Permission.ADMIN_VIEW_METRICS,
        # Role management
        Permission.ROLES_READ,
        Permission.ROLES_WRITE,
        Permission.ROLES_DELETE,
    },
}


def get_permissions_for_role(role: str) -> set[str]:
    """
    Get the set of permissions for a given role.

    Args:
        role: Role identifier

    Returns:
        Set of permission strings. Empty set if role is unknown.
    """
    return ROLE_PERMISSIONS.get(role, set())


def is_valid_role(role: str) -> bool:
    """Check if a role identifier is valid (defined in ROLE_PERMISSIONS)."""
    return role in ROLE_PERMISSIONS


def validate_role(role: str) -> str:
    """
    Validate and return a role, or raise ValueError if invalid.

    Args:
        role: Role identifier to validate

    Returns:
        The validated role string

    Raises:
        ValueError: If role is not defined
    """
    # if not is_valid_role(role):
    #     valid_roles = sorted(ROLE_PERMISSIONS.keys())
    #     raise ValueError(f"Invalid role: '{role}'. Valid roles: {valid_roles}")

    if not is_valid_role(role):
        valid_roles = ", ".join(get_all_roles())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(f"Invalid role '{role}'. " f"Valid roles: {valid_roles}"),
        )

    return role


def get_all_roles() -> list[str]:
    """Get all defined role identifiers."""
    return sorted(ROLE_PERMISSIONS.keys())


def get_all_permissions() -> set[str]:
    """Get all permissions across all roles."""
    all_perms = set()
    for perms in ROLE_PERMISSIONS.values():
        all_perms.update(perms)
    return all_perms


def get_roles_with_permission(permission: str) -> list[str]:
    """Get all roles that have a specific permission."""
    return sorted(
        role for role, perms in ROLE_PERMISSIONS.items() if permission in perms
    )


# Validation at module load time
def _validate_rbac_config() -> None:
    """Validate RBAC configuration on module import."""
    # Check all permissions in ROLE_PERMISSIONS are valid Permission enum values
    all_perms = Permission.all()
    for role, perms in ROLE_PERMISSIONS.items():
        for perm in perms:
            if perm not in all_perms:
                raise ValueError(
                    f"Role '{role}' has invalid permission: '{perm}'. "
                    f"Valid permissions: {sorted(all_perms)}"
                )

    # Check all roles in ROLE_PERMISSIONS are valid Role enum values
    all_roles = set(Role._value2member_map_.keys())
    for role in ROLE_PERMISSIONS:
        if role not in all_roles:
            raise ValueError(
                f"ROLE_PERMISSIONS contains undefined role: '{role}'. "
                f"Valid roles: {sorted(all_roles)}"
            )


# Run validation on import
_validate_rbac_config()
