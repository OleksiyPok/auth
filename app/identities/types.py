# app/identities/types.py

from enum import StrEnum


class IdentityType(StrEnum):
    EMAIL = "email"
    USERNAME = "username"
    GOOGLE = "google"
