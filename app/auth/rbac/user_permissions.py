# app/auth/rbac/user_permissions.py

"""
User permission utilities for RBAC.

This module provides functions for retrieving and managing user permissions
based on their role assignments.
"""

from typing import Awaitable, Callable

from app.auth.rbac.role_permissions import get_permissions_for_role, is_valid_role
from app.users.models import User

# Type alias for user getter function
UserGetter = Callable[..., Awaitable[User]]


def get_user_permissions(user: User) -> set[str]:
    """Get all permissions for a user based on their role."""
    if not is_valid_role(user.role):
        # Invalid role - no permissions
        return set()
    return get_permissions_for_role(user.role)


__all__ = ["get_user_permissions", "UserGetter"]
