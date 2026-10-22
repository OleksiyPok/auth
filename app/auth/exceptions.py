# app/auth/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class AuthError(AppError):
    """Base exception for auth feature."""


class InvalidAccessTokenError(AuthError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_TOKEN"
    message = "Invalid access token"


class FreshSessionRequiredError(AuthError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "FRESH_SESSION_REQUIRED"
    message = "This action requires a recent sign-in. Sign in again."


class InsufficientPermissionsError(AuthError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "INSUFFICIENT_PERMISSIONS"
    message = "Insufficient permissions to perform this action."


class InvalidRoleError(AuthError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "INVALID_ROLE"
    message = "Invalid role"
