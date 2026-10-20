# app/identities/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.auth.rbac.dependencies import require_self_identities_read
from app.core.identifiers import mask_email
from app.email_auth.models import EmailIdentity
from app.google_auth.models import GoogleIdentity
from app.identities.dependencies import get_identity_service
from app.identities.schemas import IdentityResponseSchema
from app.identities.services.service_interface import IdentityServiceInterface
from app.identities.types import IdentityType
from app.username_auth.models import UsernameIdentity
from app.users.models import User

router = APIRouter(
    prefix="/identities",
    tags=["Identities"],
)


def _to_response(
    identity: EmailIdentity | UsernameIdentity | GoogleIdentity,
) -> IdentityResponseSchema:
    if isinstance(identity, EmailIdentity):
        return IdentityResponseSchema(
            id=identity.id,
            type=IdentityType.EMAIL,
            display_identifier=mask_email(identity.email),
            created_at=identity.created_at,
        )

    if isinstance(identity, UsernameIdentity):
        return IdentityResponseSchema(
            id=identity.id,
            type=IdentityType.USERNAME,
            display_identifier=identity.username,
            created_at=identity.created_at,
        )

    return IdentityResponseSchema(
        id=identity.id,
        type=IdentityType.GOOGLE,
        display_identifier=None,
        created_at=identity.created_at,
    )


@router.get(
    "",
    summary="Get sign-in methods",
    description="Get the sign-in methods of the current user.",
    response_model=list[IdentityResponseSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_self_identities_read())],
)
async def get_identities(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        IdentityServiceInterface,
        Depends(get_identity_service),
    ],
) -> list[IdentityResponseSchema]:
    identities = await service.list_identities(current_user.id)

    return [_to_response(identity) for identity in identities]