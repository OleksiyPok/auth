from fastapi import status

from app.core.exceptions import AppError


class TwoFactorError(AppError):
    """Base exception for two-factor authentication."""


class TwoFactorChallengeNotFoundError(TwoFactorError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "TWO_FACTOR_CHALLENGE_NOT_FOUND"
    message = "Two-factor challenge not found"


class InvalidTwoFactorCodeError(TwoFactorError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_TWO_FACTOR_CODE"
    message = "Invalid two-factor code"


class TwoFactorCodeExpiredError(TwoFactorError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "TWO_FACTOR_CODE_EXPIRED"
    message = "Two-factor code expired"


class TwoFactorAlreadyEnabledError(TwoFactorError):
    status_code = status.HTTP_409_CONFLICT
    code = "TWO_FACTOR_ALREADY_ENABLED"
    message = "Two-factor authentication is already enabled"


class TwoFactorAlreadyDisabledError(TwoFactorError):
    status_code = status.HTTP_409_CONFLICT
    code = "TWO_FACTOR_ALREADY_DISABLED"
    message = "Two-factor authentication is already disabled"


class TwoFactorTooManyAttemptsError(TwoFactorError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "TWO_FACTOR_TOO_MANY_ATTEMPTS"
    message = "Too many invalid two-factor code attempts"
