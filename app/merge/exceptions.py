# app/merge/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class MergeError(AppError):
    """Base exception for merge operations."""


class MergeAccountNotFoundError(MergeError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "MERGE_ACCOUNT_NOT_FOUND"
    message = "No account found for this sign-in method"


class MergeTypeConflictError(MergeError):
    status_code = status.HTTP_409_CONFLICT
    code = "MERGE_TYPE_CONFLICT"
    message = "Both accounts have a sign-in method of the same type"


class MergeProofNotFoundError(MergeError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "MERGE_PROOF_NOT_FOUND"
    message = "Merge proof not found"


class MergeProofExpiredError(MergeError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "MERGE_PROOF_EXPIRED"
    message = "Merge proof expired"


class MergeProofUsedError(MergeError):
    status_code = status.HTTP_409_CONFLICT
    code = "MERGE_PROOF_USED"
    message = "Merge proof has already been used"


class MergeProofNotConfirmedError(MergeError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "MERGE_PROOF_NOT_CONFIRMED"
    message = "Merge proof is not confirmed with the two-factor code yet"


class MergeProofConfirmationNotRequiredError(MergeError):
    status_code = status.HTTP_409_CONFLICT
    code = "MERGE_PROOF_CONFIRMATION_NOT_REQUIRED"
    message = "This merge proof does not need a confirmation"


class InvalidMergeCredentialsError(MergeError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "MERGE_INVALID_CREDENTIALS"
    message = "Invalid credentials of the account to merge"
