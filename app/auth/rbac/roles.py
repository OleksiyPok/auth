# app/auth/rbac/roles.py

"""
Role definitions and validation for RBAC.

This module defines the Role enum and related validation functions.
Roles are named collections of permissions that users receive.
"""

from enum import StrEnum


class Role(StrEnum):
    """Built-in role identifiers."""

    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

    @classmethod
    def validate(cls, value: str) -> bool:
        """Check if a string is a valid role identifier."""
        return value in cls._value2member_map_


# Default role assigned to new users
DEFAULT_ROLE: str = Role.USER
