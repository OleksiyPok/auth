# app/email_auth/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.auth.dependencies import get_current_user
from app.email_auth.dependencies import (
    get_current_email_identity,
    get_email_login_service,
    get_email_register_service,
)
from app.email_auth.models import EmailIdentity
from app.email_auth.schemas import (
    EmailLoginRequestSchema,
    EmailRegisterRequestSchema,
    EmailRegisterResponseSchema,
)
from app.email_auth.services.login_service_interface import EmailLoginServiceInterface
from app.email_auth.services.register_service_interface import (
    EmailRegisterServiceInterface,
)
from app.sessions.schemas import AuthenticationResponseSchema
from app.two_factor.dependencies import get_two_factor_service
from app.two_factor.schemas import (
    TwoFactorChallengeResponseSchema,
    TwoFactorConfirmRequestSchema,
)
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.users.models import User

EMAIL_PROVIDER = "email"

router = APIRouter(
    prefix="/auth/email",
    tags=["Email Authentication"],
)


@router.post(
    "/register",
    response_model=EmailRegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: EmailRegisterRequestSchema,
    service: Annotated[
        EmailRegisterServiceInterface,
        Depends(get_email_register_service),
    ],
):
    return await service.register(data)


@router.post(
    "/login",
    response_model=AuthenticationResponseSchema,
)
async def login(
    request: Request,
    data: EmailLoginRequestSchema,
    service: Annotated[
        EmailLoginServiceInterface,
        Depends(get_email_login_service),
    ],
):
    return await service.login(
        data=data,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.post(
    "/login/confirm",
    response_model=AuthenticationResponseSchema,
)
async def confirm_login(
    data: TwoFactorConfirmRequestSchema,
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    return await service.confirm_login(
        challenge_id=data.challenge_id,
        code=data.code,
        provider=EMAIL_PROVIDER,
    )


@router.post(
    "/2fa/enable",
    response_model=TwoFactorChallengeResponseSchema,
)
async def enable_two_factor(
    current_user: Annotated[User, Depends(get_current_user)],
    email_identity: Annotated[
        EmailIdentity,
        Depends(get_current_email_identity),
    ],
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    return await service.request_enable(
        current_user,
        EMAIL_PROVIDER,
    )


@router.post(
    "/2fa/enable/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def confirm_enable_two_factor(
    data: TwoFactorConfirmRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    email_identity: Annotated[
        EmailIdentity,
        Depends(get_current_email_identity),
    ],
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    await service.confirm_enable(
        current_user,
        data.challenge_id,
        data.code,
        EMAIL_PROVIDER,
    )


@router.post(
    "/2fa/disable",
    response_model=TwoFactorChallengeResponseSchema,
)
async def disable_two_factor(
    current_user: Annotated[User, Depends(get_current_user)],
    email_identity: Annotated[
        EmailIdentity,
        Depends(get_current_email_identity),
    ],
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    return await service.request_disable(
        current_user,
        EMAIL_PROVIDER,
    )


@router.post(
    "/2fa/disable/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def confirm_disable_two_factor(
    data: TwoFactorConfirmRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    email_identity: Annotated[
        EmailIdentity,
        Depends(get_current_email_identity),
    ],
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    await service.confirm_disable(
        current_user,
        data.challenge_id,
        data.code,
        EMAIL_PROVIDER,
    )
