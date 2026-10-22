# app/users/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class UserError(AppError):
    """Base exception for users feature."""


class UserNotFoundError(UserError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "USER_NOT_FOUND"
    message = "User not found"


class UserAlreadyExistsError(UserError):
    status_code = status.HTTP_409_CONFLICT
    code = "USER_ALREADY_EXISTS"
    message = "User already exists"


class CannotChangeOwnRoleError(UserError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "CANNOT_CHANGE_OWN_ROLE"
    message = "You cannot change your own role"


class LastSuperadminDeactivationError(UserError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "LAST_SUPERADMIN_DEACTIVATION"
    message = "Cannot deactivate the last superadmin"


class UserAlreadyDeactivatedError(UserError):
    status_code = status.HTTP_409_CONFLICT
    code = "USER_ALREADY_DEACTIVATED"
    message = "User is already deactivated"

class CannotPurgeActiveUserError(UserError):
    status_code = status.HTTP_409_CONFLICT
    code = "USER_STILL_ACTIVE"
    message = "An active user cannot be purged; deactivate the user first"

class PurgeConfirmationMismatchError(UserError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "PURGE_CONFIRMATION_MISMATCH"
    message = "confirm_user_id must equal the user id"

class InactiveUserError(UserError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "USER_INACTIVE"
    message = "User is inactive"


class CannotDeactivateSelfError(UserError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "CANNOT_DEACTIVATE_SELF_ROLE"
    message = "Cannot deactivate the self role"
