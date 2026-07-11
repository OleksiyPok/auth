# app/auth/router.py

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_auth_service
from app.auth.schemas import RegisterRequestSchema, RegisterResponseSchema
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
