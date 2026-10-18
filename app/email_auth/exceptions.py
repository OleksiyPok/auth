# app/email_auth/exceptions.py

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



class EmailRegistrationNotFoundError(EmailAuthError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "EMAIL_REGISTRATION_NOT_FOUND"
    message = "Email registration not found"


class InvalidEmailVerificationCodeError(EmailAuthError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_EMAIL_VERIFICATION_CODE"
    message = "Invalid email verification code"


class EmailVerificationCodeExpiredError(EmailAuthError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "EMAIL_VERIFICATION_CODE_EXPIRED"
    message = "Email verification code expired"


class EmailVerificationTooManyAttemptsError(EmailAuthError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "EMAIL_VERIFICATION_TOO_MANY_ATTEMPTS"
    message = "Too many invalid email verification code attempts"