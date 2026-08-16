# app/username_auth/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.username_auth.dependencies import (
    get_username_login_service,
    get_username_register_service,
)
from app.username_auth.schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
)
from app.username_auth.services.login_service_interface import UsernameLoginServiceInterface
from app.username_auth.services.register_service_interface import (
    UsernameRegisterServiceInterface,
)
from app.sessions.schemas import AuthenticationResponseSchema

router = APIRouter(
    prefix="/auth",
    tags=["Local Authentication"],
)


@router.post(
    "/register",
    summary="Register user account",
    description="Creates a new user account using local authentication.",
    response_model=RegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequestSchema,
    service: Annotated[
        UsernameRegisterServiceInterface,
        Depends(get_username_register_service),
    ],
):
    return await service.register(data)


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
        UsernameLoginServiceInterface,
        Depends(get_username_login_service),
    ],
):
    data = LoginRequestSchema(
        login=form_data.username,
        password=form_data.password,
    )

    return await service.login(
        data=data,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
