# app/google_auth/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.rate_limit import LOGIN_IP, limit_by_ip
from app.google_auth.dependencies import get_google_auth_service
from app.google_auth.schemas import (
    GoogleAuthorizationResponseSchema,
    GoogleCallbackResponse,
)
from app.google_auth.services.service_interface import GoogleAuthServiceInterface

router = APIRouter(
    prefix="/auth/google",
    tags=["Google Authentication"],
)


@router.post(
    "/login",
    response_model=GoogleAuthorizationResponseSchema,
)
async def google_login(
    service: Annotated[
        GoogleAuthServiceInterface,
        Depends(get_google_auth_service),
    ],
):
    authorization_url = await service.create_authorization_url()

    return GoogleAuthorizationResponseSchema(
        authorization_url=authorization_url,
    )


@router.get(
    "/callback",
    response_model=GoogleCallbackResponse,
    dependencies=[Depends(limit_by_ip(LOGIN_IP))],
)
async def google_callback(
    request: Request,
    code: str,
    state: str,
    service: Annotated[
        GoogleAuthServiceInterface,
        Depends(get_google_auth_service),
    ],
):
    return await service.handle_callback(
        code=code,
        state=state,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
