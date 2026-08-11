# app/google_auth/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class GoogleAuthError(AppError):
    """Base exception for Google authentication errors."""


class GoogleOAuthStateError(GoogleAuthError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "GOOGLE_OAUTH_STATE_INVALID"
    message = "Invalid or expired Google OAuth state"


class GoogleIdentityAlreadyConnectedError(GoogleAuthError):
    status_code = status.HTTP_409_CONFLICT
    code = "GOOGLE_IDENTITY_ALREADY_CONNECTED"
    message = "Google account is already connected to another user"
