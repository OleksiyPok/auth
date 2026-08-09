# app/auth/router.py

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import (
    get_login_service,
    get_register_service,
    get_token_service,
)
from app.auth.schemas import (
    LoginRequestSchema,
    RefreshTokenRequestSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
    TokenResponseSchema,
)
from app.auth.services.login_service_interface import LoginServiceInterface
from app.auth.services.register_service_interface import RegisterServiceInterface
from app.auth.services.token_service_interface import TokenServiceInterface

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    summary="Register user account",
    description="Creates a new user account.",
    response_model=RegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequestSchema,
    service: RegisterServiceInterface = Depends(get_register_service),
):
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponseSchema,
)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: LoginServiceInterface = Depends(get_login_service),
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


@router.post(
    "/refresh",
    response_model=TokenResponseSchema,
)
async def refresh(
    data: RefreshTokenRequestSchema,
    service: TokenServiceInterface = Depends(get_token_service),
):

    return await service.refresh(data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: RefreshTokenRequestSchema,
    service: LoginServiceInterface = Depends(get_login_service),
):

    await service.logout(data.refresh_token)
