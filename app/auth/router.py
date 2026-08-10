# app/auth/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_token_service
from app.auth.schemas import RefreshTokenRequestSchema, TokenResponseSchema
from app.auth.services.token_service_interface import TokenServiceInterface
from app.sessions.dependencies import get_sessions_service
from app.sessions.services.service_interface import SessionServiceInterface

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/refresh",
    response_model=TokenResponseSchema,
)
async def refresh(
    data: RefreshTokenRequestSchema,
    service: Annotated[
        TokenServiceInterface,
        Depends(get_token_service),
    ],
):
    return await service.refresh(
        data.refresh_token,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: RefreshTokenRequestSchema,
    service: Annotated[
        SessionServiceInterface,
        Depends(get_sessions_service),
    ],
):
    await service.logout(
        data.refresh_token,
    )
