# app/sessions/exceptions.py


class SessionError(Exception):
    pass


class SessionNotFoundError(SessionError):
    pass


class SessionRevokedError(SessionError):
    pass


class SessionExpiredError(SessionError):
    pass


class InvalidRefreshTokenError(SessionError):
    pass


class SessionAccessDeniedError(SessionError):
    pass
