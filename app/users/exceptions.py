# app/users/exceptions.py

from app.core.exceptions import DomainError


class UserError(DomainError):
    pass


class UserNotFoundError(UserError):
    code = "USER_NOT_FOUND"
    message = "User not found"
    status_code = 404
