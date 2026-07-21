# app/users/enums.py

from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
