# app/merge/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.auth.rbac.dependencies import require_self_identities_write
from app.core.rate_limit import CONFIRM_IP, LOGIN_IP, limit_by_ip
from app.google_auth.dependencies import get_google_auth_service
from app.google_auth.purpose import GoogleOAuthPurpose
from app.google_auth.schemas import GoogleAuthorizationResponseSchema
from app.google_auth.services.service_interface import GoogleAuthServiceInterface
from app.merge.dependencies import get_merge_proof_service
from app.merge.schemas import (
    MergeProofConfirmRequestSchema,
    MergeProofEmailRequestSchema,
    MergeProofResponseSchema,
    MergeProofUsernameRequestSchema,
)
from app.merge.services.proof_service_interface import MergeProofServiceInterface
from app.users.models import User

router = APIRouter(
    prefix="/users/me/merge",
    tags=["Merge"],
)


@router.post(
    "/proofs/username",
    summary="Prove an account by username and password",
    description=(
        "Create a short-lived single-use proof that the current user controls "
        "another account, using the username and password of that account."
    ),
    response_model=MergeProofResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_self_identities_write()),
        Depends(limit_by_ip(LOGIN_IP)),
    ],
)
async def create_proof_by_username(
    data: MergeProofUsernameRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[MergeProofServiceInterface, Depends(get_merge_proof_service)],
) -> MergeProofResponseSchema:
    return await service.create_by_username(current_user, data)


@router.post(
    "/proofs/email",
    summary="Prove an account by email and password",
    description=(
        "Create a short-lived single-use proof that the current user controls "
        "another account, using the email and password of that account."
    ),
    response_model=MergeProofResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_self_identities_write()),
        Depends(limit_by_ip(LOGIN_IP)),
    ],
)
async def create_proof_by_email(
    data: MergeProofEmailRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[MergeProofServiceInterface, Depends(get_merge_proof_service)],
) -> MergeProofResponseSchema:
    return await service.create_by_email(current_user, data)


@router.post(
    "/proofs/google",
    summary="Prove an account by Google: start",
    description=(
        "Get the Google authorization URL. After the sign-in at Google, the "
        "callback returns a short-lived single-use proof for the account that "
        "owns that Google account."
    ),
    response_model=GoogleAuthorizationResponseSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_self_identities_write()),
        Depends(limit_by_ip(LOGIN_IP)),
    ],
)
async def start_merge_proof_by_google(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GoogleAuthServiceInterface, Depends(get_google_auth_service)],
) -> GoogleAuthorizationResponseSchema:
    authorization_url = await service.create_authorization_url(
        purpose=GoogleOAuthPurpose.MERGE,
        user_id=current_user.id,
    )

    return GoogleAuthorizationResponseSchema(
        authorization_url=authorization_url,
    )


@router.post(
    "/proofs/confirm",
    summary="Confirm a merge proof with the two-factor code",
    description=(
        "When the proven account has two-factor authentication, enter the code "
        "that was sent to it to make the proof usable."
    ),
    response_model=MergeProofResponseSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_self_identities_write()),
        Depends(limit_by_ip(CONFIRM_IP)),
    ],
)
async def confirm_merge_proof(
    data: MergeProofConfirmRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[MergeProofServiceInterface, Depends(get_merge_proof_service)],
) -> MergeProofResponseSchema:
    return await service.confirm(current_user, data)
