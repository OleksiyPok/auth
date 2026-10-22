# app/auth/rbac/permissions.py

"""
Permission definitions and validation for RBAC.

This module defines the Permission enum and related validation functions.
Permissions are the atomic unit of authorization - stable, validated identifiers.
"""

from enum import StrEnum


class Permission(StrEnum):
    """
    Stable permission identifiers.

    Naming convention: RESOURCE_ACTION
    - RESOURCE: plural noun (users, sessions, roles, admin, self)
    - ACTION: read, write, delete, deactivate, manage, revoke, access

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
    USERS_DEACTIVATE = "users.deactivate"
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
    SELF_DEACTIVATE = "self.deactivate"
    SELF_SESSIONS_READ = "self.sessions.read"
    SELF_SESSIONS_REVOKE = "self.sessions.revoke"
    SELF_IDENTITIES_READ = "self.identities.read"
    SELF_IDENTITIES_WRITE = "self.identities.write"

    @classmethod
    def validate(cls, value: str) -> bool:
        """Check if a string is a valid permission identifier."""
        return value in cls._value2member_map_

    @classmethod
    def all(cls) -> set[str]:
        """Return all defined permissions as a set."""
        return set(cls._value2member_map_.keys())
