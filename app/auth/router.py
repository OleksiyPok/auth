# app/auth/router.py

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import get_auth_service
from app.auth.schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
    TokenResponseSchema,
)
from app.auth.service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register/",
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
