# app/email_auth/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.email_auth.dependencies import (
    get_email_login_service,
    get_email_register_service,
)
from app.email_auth.schemas import (
    EmailLoginRequestSchema,
    EmailRegisterChallengeResponseSchema,
    EmailRegisterConfirmRequestSchema,
    EmailRegisterResendRequestSchema,
    EmailRegisterRequestSchema,
    EmailRegisterResponseSchema,
)
from app.email_auth.services.login_service_interface import EmailLoginServiceInterface
from app.email_auth.services.register_service_interface import (
    EmailRegisterServiceInterface,
)
from app.sessions.schemas import AuthenticationResponseSchema

router = APIRouter(
    prefix="/auth/email",
    tags=["Email Authentication"],
)


@router.post(
    "/register",
    response_model=EmailRegisterChallengeResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
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
    "/register/resend",
    response_model=EmailRegisterChallengeResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def resend_register_code(
    data: EmailRegisterResendRequestSchema,
    service: Annotated[
        EmailRegisterServiceInterface,
        Depends(get_email_register_service),
    ],
):
    return await service.resend(data)

@router.post(
    "/register/confirm",
    response_model=EmailRegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def confirm_register(
    data: EmailRegisterConfirmRequestSchema,
    service: Annotated[
        EmailRegisterServiceInterface,
        Depends(get_email_register_service),
    ],
):
    return await service.confirm(data)


@router.post(
    "/login",
    response_model=AuthenticationResponseSchema,
)
async def login(
    request: Request,
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    service: Annotated[
        EmailLoginServiceInterface,
        Depends(get_email_login_service),
    ],
):
    data = EmailLoginRequestSchema(
        email=form_data.username,
        password=form_data.password,
    )

    return await service.login(
        data=data,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
