# app/merge/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class MergeError(AppError):
    """Base exception for merge operations."""


class MergeAccountNotFoundError(MergeError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "MERGE_ACCOUNT_NOT_FOUND"
    message = "No account found for this sign-in method"


class InvalidMergeCredentialsError(MergeError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "MERGE_INVALID_CREDENTIALS"
    message = "Invalid credentials of the account to merge"
