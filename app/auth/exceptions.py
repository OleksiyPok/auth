# app/auth/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class AuthError(AppError):
    """Base exception for auth feature."""


class InvalidCredentialsError(AuthError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_CREDENTIALS"
    message = "Invalid credentials"


class InvalidAccessTokenError(AuthError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_TOKEN"
    message = "Invalid access token"


class InsufficientPermissionsError(AuthError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "INSUFFICIENT_PERMISSIONS"
    message = "Insufficient permissions to perform this action."
