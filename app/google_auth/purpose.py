# app/google_auth/purpose.py

from enum import StrEnum


class GoogleOAuthPurpose(StrEnum):
    """What a Google OAuth state was created for."""

    LOGIN = "login"
    LINK = "link"
