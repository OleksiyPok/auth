# app/username_auth/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.identifiers import normalize_username
from app.core.rate_limit import (
    LOGIN_IP,
    LOGIN_USERNAME,
    REGISTER_IP,
    REGISTER_USERNAME,
    limit_by_ip,
    rate_limiter,
)
from app.sessions.schemas import AuthenticationResponseSchema
from app.username_auth.dependencies import (
    get_username_login_service,
    get_username_register_service,
)
from app.username_auth.schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
)
from app.username_auth.services.login_service_interface import (
    UsernameLoginServiceInterface,
)
from app.username_auth.services.register_service_interface import (
    UsernameRegisterServiceInterface,
)

router = APIRouter(
    prefix="/auth/username",
    tags=["Username Authentication"],
)


@router.post(
    "/register",
    summary="Register user account",
    description="Creates a new user account using username authentication.",
    response_model=RegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limit_by_ip(REGISTER_IP))],
)
async def register(
    data: RegisterRequestSchema,
    service: Annotated[
        UsernameRegisterServiceInterface,
        Depends(get_username_register_service),
    ],
):
    rate_limiter.hit(REGISTER_USERNAME, normalize_username(data.username))
    return await service.register(data)


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
        UsernameLoginServiceInterface,
        Depends(get_username_login_service),
    ],
):
    rate_limiter.hit(LOGIN_USERNAME, normalize_username(form_data.username))

    data = LoginRequestSchema(
        username=form_data.username,
        password=form_data.password,
    )

    return await service.login(
        data=data,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
