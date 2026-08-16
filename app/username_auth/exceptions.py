# app/username_auth/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class UsernameAuthError(AppError):
    """Base exception for username authentication."""


class InvalidCredentialsError(UsernameAuthError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_CREDENTIALS"
    message = "Invalid credentials"


class UsernameIdentityNotFoundError(UsernameAuthError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "USERNAME_IDENTITY_NOT_FOUND"
    message = "Username identity not found"
