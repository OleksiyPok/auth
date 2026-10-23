# app/identities/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.auth.rbac.dependencies import (
    require_self_identities_read,
    require_self_identities_write,
)
from app.core.identifiers import mask_email
from app.email_auth.dependencies import get_email_link_service
from app.email_auth.models import EmailIdentity
from app.email_auth.schemas import (
    EmailLinkChallengeResponseSchema,
    EmailLinkRequestSchema,
)
from app.email_auth.services.link_service_interface import EmailLinkServiceInterface
from app.google_auth.models import GoogleIdentity
from app.identities.dependencies import get_identity_service
from app.identities.schemas import IdentityResponseSchema, LinkUsernameRequestSchema
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


@router.post(
    "/username",
    summary="Link a username",
    description="Add a username and password sign-in method to the current user.",
    response_model=IdentityResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_self_identities_write())],
)
async def link_username(
    data: LinkUsernameRequestSchema,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        IdentityServiceInterface,
        Depends(get_identity_service),
    ],
) -> IdentityResponseSchema:
    identity = await service.link_username(
        user_id=current_user.id,
        username=data.username,
        password=data.password,
    )

    return _to_response(identity)



@router.post(
    "/email",
    summary="Link an email: request",
    description=(
        "Start adding an email and password sign-in method to the current user. "
        "A verification code is sent to the address."
    ),
    response_model=EmailLinkChallengeResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_self_identities_write())],
)
async def request_email_link(
    data: EmailLinkRequestSchema,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        EmailLinkServiceInterface,
        Depends(get_email_link_service),
    ],
) -> EmailLinkChallengeResponseSchema:
    return await service.request_link(current_user.id, data)