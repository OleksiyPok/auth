# app/users/status.py

"""
User status definitions.

A user is either active or deactivated; the status also records why.
"""

from enum import StrEnum


class UserStatus(StrEnum):
    """Lifecycle status of a user."""

    ACTIVE = "active"
    DEACTIVATED_BY_ADMIN = "deactivated_by_admin"
    DEACTIVATED_BY_USER = "deactivated_by_user"
    DEACTIVATED_BY_MERGE = "deactivated_by_merge"