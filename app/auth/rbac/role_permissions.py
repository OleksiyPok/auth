# app/auth/rbac/role_permissions.py

"""
Role-to-permission mapping for RBAC.

This module contains the declarative role -> permissions mapping.
This is the single source of truth for what permissions each role has.
"""

from typing import Final

from app.auth.rbac.permissions import Permission
from app.auth.rbac.roles import Role

__all__ = [
    "ROLE_PERMISSIONS",
    "get_permissions_for_role",
    "is_valid_role",
    "get_all_roles",
    "get_all_permissions",
    "get_roles_with_permission",
    "validate_role",
]

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
    if not is_valid_role(role):
        valid_roles = ", ".join(get_all_roles())
        raise ValueError(f"Invalid role '{role}'. Valid roles: {valid_roles}")

    return role


# Validation at module load time
def _validate_rbac_config() -> None:
    """Validate RBAC configuration on module import."""
    from app.auth.rbac.permissions import Permission as PermissionEnum

    # Check all permissions in ROLE_PERMISSIONS are valid Permission enum values
    all_perms = PermissionEnum.all()
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
