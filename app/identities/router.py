# app/identities/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import (
    get_current_session,
    get_current_user,
    require_fresh_session,
)
from app.auth.rbac.dependencies import (
    require_self_identities_read,
    require_self_identities_write,
)
from app.core.identifiers import mask_email, normalize_email
from app.core.rate_limit import (
    CONFIRM_IP,
    LINK_EMAIL,
    LINK_IP,
    UNLINK_IP,
    limit_by_ip,
    rate_limiter,
)
from app.email_auth.dependencies import get_email_link_service
from app.email_auth.models import EmailIdentity
from app.email_auth.schemas import (
    EmailLinkChallengeResponseSchema,
    EmailLinkConfirmRequestSchema,
    EmailLinkRequestSchema,
)
from app.email_auth.services.link_service_interface import EmailLinkServiceInterface
from app.google_auth.dependencies import get_google_auth_service
from app.google_auth.models import GoogleIdentity
from app.google_auth.purpose import GoogleOAuthPurpose
from app.google_auth.schemas import GoogleAuthorizationResponseSchema
from app.google_auth.services.service_interface import GoogleAuthServiceInterface
from app.identities.dependencies import get_identity_service
from app.identities.schemas import IdentityResponseSchema, LinkUsernameRequestSchema
from app.identities.services.service_interface import IdentityServiceInterface
from app.identities.types import IdentityType
from app.sessions.schemas import CurrentSessionSchema
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


@router.delete(
    "/{identity_id}",
    summary="Remove a sign-in method",
    description=(
        "Remove a sign-in method of the current user. The last method and the "
        "method used by the current session cannot be removed. Sessions "
        "created through the removed method are revoked."
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(limit_by_ip(UNLINK_IP)),
        Depends(require_fresh_session),
        Depends(require_self_identities_write()),
    ],
)
async def unlink_identity(
    identity_id: str,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    current_session: Annotated[
        CurrentSessionSchema,
        Depends(get_current_session),
    ],
    service: Annotated[
        IdentityServiceInterface,
        Depends(get_identity_service),
    ],
) -> None:
    await service.unlink_identity(
        user_id=current_user.id,
        identity_id=identity_id,
        current_identity_id=current_session.identity_id,
    )


@router.post(
    "/username",
    summary="Link a username",
    description="Add a username and password sign-in method to the current user.",
    response_model=IdentityResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(limit_by_ip(LINK_IP)),
        Depends(require_fresh_session),
        Depends(require_self_identities_write()),
    ],
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
    dependencies=[
        Depends(limit_by_ip(LINK_IP)),
        Depends(require_fresh_session),
        Depends(require_self_identities_write()),
    ],
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
    rate_limiter.hit(LINK_EMAIL, normalize_email(data.email))
    return await service.request_link(current_user.id, data)


@router.post(
    "/email/confirm",
    summary="Link an email: confirm",
    description=(
        "Confirm the code and add the email sign-in method to the current user."
    ),
    response_model=IdentityResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(limit_by_ip(CONFIRM_IP)),
        Depends(require_fresh_session),
        Depends(require_self_identities_write()),
    ],
)
async def confirm_email_link(
    data: EmailLinkConfirmRequestSchema,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        EmailLinkServiceInterface,
        Depends(get_email_link_service),
    ],
) -> IdentityResponseSchema:
    identity = await service.confirm_link(current_user.id, data)

    return _to_response(identity)


@router.post(
    "/google",
    summary="Link a Google account: start",
    description=(
        "Get the Google authorization URL. After the sign-in at Google, the "
        "callback adds the Google account to the current user."
    ),
    response_model=GoogleAuthorizationResponseSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(limit_by_ip(LINK_IP)),
        Depends(require_fresh_session),
        Depends(require_self_identities_write()),
    ],
)
async def start_google_link(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        GoogleAuthServiceInterface,
        Depends(get_google_auth_service),
    ],
) -> GoogleAuthorizationResponseSchema:
    authorization_url = await service.create_authorization_url(
        purpose=GoogleOAuthPurpose.LINK,
        user_id=current_user.id,
    )

    return GoogleAuthorizationResponseSchema(
        authorization_url=authorization_url,
    )
