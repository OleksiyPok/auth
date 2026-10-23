# app/merge/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.auth.rbac.dependencies import require_self_identities_write
from app.core.rate_limit import LOGIN_IP, limit_by_ip
from app.merge.dependencies import get_merge_proof_service
from app.merge.schemas import (
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
