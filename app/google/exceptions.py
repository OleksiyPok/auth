# app/google/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class GoogleError(AppError):
    """Base exception for Google application errors."""


class GoogleOAuthStateError(GoogleError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "GOOGLE_OAUTH_STATE_INVALID"
    message = "Invalid or expired Google OAuth state"


class GoogleAccountAlreadyConnectedError(GoogleError):
    status_code = status.HTTP_409_CONFLICT
    code = "GOOGLE_ACCOUNT_ALREADY_CONNECTED"
    message = "Google account is already connected to another user"


class GoogleAccountNotFoundError(GoogleError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "GOOGLE_ACCOUNT_NOT_FOUND"
    message = "Google account is not connected"


class GoogleAPIError(GoogleError):
    status_code = status.HTTP_502_BAD_GATEWAY
    code = "GOOGLE_API_ERROR"
    message = "Google API request failed"
