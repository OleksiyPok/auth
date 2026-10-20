# app/email_auth/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.identifiers import normalize_email
from app.core.rate_limit import (
    CONFIRM_IP,
    LOGIN_EMAIL,
    LOGIN_IP,
    REGISTER_EMAIL,
    REGISTER_IP,
    SEND_CODE_IP,
    limit_by_ip,
    rate_limiter,
)
from app.email_auth.dependencies import (
    get_email_login_service,
    get_email_register_service,
)
from app.email_auth.schemas import (
    EmailLoginRequestSchema,
    EmailRegisterChallengeResponseSchema,
    EmailRegisterConfirmRequestSchema,
    EmailRegisterRequestSchema,
    EmailRegisterResendRequestSchema,
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
    dependencies=[Depends(limit_by_ip(REGISTER_IP))],
)
async def register(
    data: EmailRegisterRequestSchema,
    service: Annotated[
        EmailRegisterServiceInterface,
        Depends(get_email_register_service),
    ],
):
    rate_limiter.hit(REGISTER_EMAIL, normalize_email(data.email))
    return await service.register(data)


@router.post(
    "/register/resend",
    response_model=EmailRegisterChallengeResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(limit_by_ip(SEND_CODE_IP))],
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
    dependencies=[Depends(limit_by_ip(CONFIRM_IP))],
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
    dependencies=[Depends(limit_by_ip(LOGIN_IP))],
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
    rate_limiter.hit(LOGIN_EMAIL, normalize_email(form_data.username))

    data = EmailLoginRequestSchema(
        email=form_data.username,
        password=form_data.password,
    )

    return await service.login(
        data=data,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
