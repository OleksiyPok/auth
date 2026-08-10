# app/local_auth/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schemas import TokenResponseSchema
from app.local_auth.dependencies import (
    get_local_login_service,
    get_local_register_service,
)
from app.local_auth.login_service_interface import LocalLoginServiceInterface
from app.local_auth.register_service_interface import LocalRegisterServiceInterface
from app.local_auth.schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
)

router = APIRouter(
    prefix="/auth",
    tags=["Local Auth"],
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
        LocalRegisterServiceInterface,
        Depends(get_local_register_service),
    ],
):
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponseSchema,
)
async def login(
    request: Request,
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    service: Annotated[
        LocalLoginServiceInterface,
        Depends(get_local_login_service),
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
