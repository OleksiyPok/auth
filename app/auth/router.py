# app/auth/router.py

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import get_auth_service, get_current_user
from app.auth.schemas import (
    LoginRequestSchema,
    RefreshTokenRequestSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
    TokenResponseSchema,
)
from app.auth.service import AuthService
from app.sessions.schemas import SessionResponseSchema
from app.users.models import User

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
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponseSchema,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    data = LoginRequestSchema(
        login=form_data.username,
        password=form_data.password,
    )

    return await service.login(data)


@router.post(
    "/refresh",
    response_model=TokenResponseSchema,
)
async def refresh(
    data: RefreshTokenRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    return await service.refresh(data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: RefreshTokenRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    await service.logout(
        data.refresh_token,
    )


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_all(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    await service.logout_all(
        current_user,
    )

@router.get(
    "/sessions",
    response_model=list[SessionResponseSchema],
)
async def get_sessions(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    return await service.get_sessions(
        current_user,
    )