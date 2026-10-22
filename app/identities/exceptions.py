# app/identities/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class IdentityError(AppError):
    """Base exception for identity operations."""


class IdentityTypeConflictError(IdentityError):
    status_code = status.HTTP_409_CONFLICT
    code = "IDENTITY_TYPE_CONFLICT"
    message = "The user already has an identity of this type"


class IdentityAlreadyOwnedError(IdentityError):
    status_code = status.HTTP_409_CONFLICT
    code = "IDENTITY_ALREADY_OWNED"
    message = "The identity already belongs to this user"


class IdentityConflictError(IdentityError):
    status_code = status.HTTP_409_CONFLICT
    code = "IDENTITY_CONFLICT"
    message = "An identity with this identifier already exists"
