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


class IdentityNotFoundError(IdentityError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "IDENTITY_NOT_FOUND"
    message = "Sign-in method not found"


class IdentityNotOwnedError(IdentityError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "IDENTITY_NOT_OWNED"
    message = "The sign-in method belongs to another user"


class LastIdentityError(IdentityError):
    status_code = status.HTTP_409_CONFLICT
    code = "LAST_IDENTITY"
    message = "The last sign-in method cannot be removed"


class CurrentIdentityError(IdentityError):
    status_code = status.HTTP_409_CONFLICT
    code = "CURRENT_IDENTITY"
    message = "The sign-in method used by the current session cannot be removed"


class IdentityConflictError(IdentityError):
    status_code = status.HTTP_409_CONFLICT
    code = "IDENTITY_CONFLICT"
    message = "An identity with this identifier already exists"
