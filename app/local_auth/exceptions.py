# app/local_auth/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class LocalAuthError(AppError):
    """Base exception for local authentication."""


class LocalIdentityNotFoundError(LocalAuthError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "LOCAL_IDENTITY_NOT_FOUND"
    message = "Local identity not found"
