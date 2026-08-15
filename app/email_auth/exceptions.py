from fastapi import status

from app.core.exceptions import AppError


class EmailAuthError(AppError):
    """Base exception for email authentication."""


class InvalidEmailCredentialsError(EmailAuthError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_EMAIL_CREDENTIALS"
    message = "Invalid email or password"


class EmailIdentityNotFoundError(EmailAuthError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "EMAIL_IDENTITY_NOT_FOUND"
    message = "Email identity not found"
