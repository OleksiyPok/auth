# app/sessions/exceptions.py

from app.core.exceptions import DomainError


class SessionError(DomainError):
    pass


class SessionNotFoundError(SessionError):
    code = "SESSION_NOT_FOUND"
    message = "Session not found"
    status_code = 404


class SessionRevokedError(SessionError):
    code = "SESSION_REVOKED"
    message = "Session revoked"
    status_code = 401


class SessionExpiredError(SessionError):
    code = "SESSION_EXPIRED"
    message = "Session expired"
    status_code = 401


class InvalidRefreshTokenError(SessionError):
    code = "INVALID_REFRESH_TOKEN"
    message = "Invalid refresh token"
    status_code = 401


class SessionAccessDeniedError(SessionError):
    code = "ACCESS_DENIED"
    message = "Access denied"
    status_code = 403
