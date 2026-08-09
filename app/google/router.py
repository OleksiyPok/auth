# app/google/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.google.dependencies import get_google_service
from app.google.schemas import GoogleContactCreateSchema, GoogleContactResponseSchema
from app.google.service_interface import GoogleServiceInterface
from app.users.models import User

router = APIRouter(
    prefix="/google",
    tags=["Google"],
)


@router.post(
    "/connect",
)
async def google_authorize(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        GoogleServiceInterface,
        Depends(get_google_service),
    ],
):
    authorization_url = await service.create_authorization_url(
        current_user,
    )

    return {
        "authorization_url": authorization_url,
    }


@router.get(
    "/callback",
)
async def google_callback(
    code: str,
    state: str,
    service: Annotated[
        GoogleServiceInterface,
        Depends(get_google_service),
    ],
):
    await service.handle_callback(
        code=code,
        state=state,
    )

    return {
        "status": "connected",
    }


@router.get(
    "/contacts",
    response_model=list[GoogleContactResponseSchema],
)
async def get_google_contacts(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        GoogleServiceInterface,
        Depends(get_google_service),
    ],
):
    return await service.get_contacts(
        current_user,
    )


@router.post(
    "/contacts",
    response_model=GoogleContactResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_google_contact(
    data: GoogleContactCreateSchema,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: Annotated[
        GoogleServiceInterface,
        Depends(get_google_service),
    ],
):
    return await service.create_contact(
        current_user,
        data,
    )
