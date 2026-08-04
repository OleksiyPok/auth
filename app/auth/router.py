# app/auth/router.py

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import (
    get_authentication_service,
    get_login_service,
    get_register_service,
)
from app.auth.schemas import (
    LoginRequestSchema,
    RefreshTokenRequestSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
    TokenResponseSchema,
)
from app.auth.services.login_service import LoginService
from app.auth.services.register_service import RegisterService
from app.auth.services.token_service import TokenService

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
    # service: AuthService = Depends(get_auth_service),
    service: RegisterService = Depends(get_register_service),
):
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponseSchema,
)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    # service: AuthService = Depends(get_auth_service),
    service: LoginService = Depends(get_login_service),
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
    # service: AuthService = Depends(get_auth_service),
    service: TokenService = Depends(get_authentication_service),
):

    return await service.refresh(data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: RefreshTokenRequestSchema,
    # service: AuthService = Depends(get_auth_service),
    service: LoginService = Depends(get_login_service),
):

    await service.logout(data.refresh_token)
