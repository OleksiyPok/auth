# app/sessions/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class SessionError(AppError):
    """Base exception for sessions feature."""

    pass


class SessionNotFoundError(SessionError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "SESSION_NOT_FOUND"
    message = "Session not found"


class SessionRevokedError(SessionError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "SESSION_REVOKED"
    message = "Session revoked"


class SessionExpiredError(SessionError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "SESSION_EXPIRED"
    message = "Session expired"


class InvalidRefreshTokenError(SessionError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_REFRESH_TOKEN"
    message = "Invalid refresh token"


class SessionAccessDeniedError(SessionError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "SESSION_ACCESS_DENIED"
    message = "Session access denied"
