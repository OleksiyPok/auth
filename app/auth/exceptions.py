# app/auth/exceptions.py

from app.core.exceptions import DomainError


class AuthError(DomainError):
    pass


class UserAlreadyExistsError(AuthError):
    code = "USER_ALREADY_EXISTS"
    message = "User already exists"
    status_code = 409


class InvalidCredentialsError(AuthError):
    code = "INVALID_CREDENTIALS"
    message = "Invalid login or password"
    status_code = 401


class InvalidTokenError(AuthError):
    code = "INVALID_TOKEN"
    message = "Invalid access token"
    status_code = 401


class InvalidTokenPayloadError(AuthError):
    code = "INVALID_TOKEN"
    message = "Invalid token payload"
    status_code = 401


class SessionNotFoundAuthError(AuthError):
    code = "SESSION_NOT_FOUND"
    message = "Session not found"
    status_code = 401


class UserInactiveError(AuthError):
    code = "USER_INACTIVE"
    message = "User is inactive"
    status_code = 403


class AuthenticatedUserNotFoundError(AuthError):
    code = "USER_NOT_FOUND"
    message = "User not found"
    status_code = 401


class InsufficientPermissionsError(AuthError):
    code = "ACCESS_DENIED"
    message = "Access denied"
    status_code = 403
