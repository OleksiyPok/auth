# app/identities/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class IdentityError(AppError):
    """Base exception for identity operations."""


class IdentityTypeConflictError(IdentityError):
    status_code = status.HTTP_409_CONFLICT
    code = "IDENTITY_TYPE_CONFLICT"
    message = "The user already has an identity of this type"