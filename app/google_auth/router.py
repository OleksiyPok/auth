# app/google_auth/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import get_current_user
from app.google_auth.dependencies import get_google_auth_service
from app.google_auth.schemas import (
    GoogleAuthorizationResponseSchema,
    GoogleConnectionStatusSchema,
)
from app.google_auth.service_interface import GoogleAuthServiceInterface
from app.sessions.schemas import TokenResponseSchema
from app.users.models import User

router = APIRouter(
    prefix="/google/auth",
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


@router.post(
    "/connect",
    response_model=GoogleAuthorizationResponseSchema,
)
async def google_connect(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        GoogleAuthServiceInterface,
        Depends(get_google_auth_service),
    ],
):
    authorization_url = await service.create_authorization_url(
        current_user,
    )

    return GoogleAuthorizationResponseSchema(
        authorization_url=authorization_url,
    )


@router.get(
    "/callback",
    response_model=TokenResponseSchema | None,
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


@router.get(
    "/status",
    response_model=GoogleConnectionStatusSchema,
)
async def google_connection_status(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        GoogleAuthServiceInterface,
        Depends(get_google_auth_service),
    ],
):
    return await service.get_connection_status(
        current_user,
    )
