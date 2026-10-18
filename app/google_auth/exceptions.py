# app/google_auth/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class GoogleAuthError(AppError):
    """Base exception for Google authentication errors."""


class GoogleOAuthStateError(GoogleAuthError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "GOOGLE_OAUTH_STATE_INVALID"
    message = "Invalid or expired Google OAuth state"



class GoogleEmailNotVerifiedError(GoogleAuthError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "GOOGLE_EMAIL_NOT_VERIFIED"
    message = "The email address of your Google account is not verified"