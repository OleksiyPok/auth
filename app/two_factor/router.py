from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.two_factor.dependencies import get_two_factor_service
from app.two_factor.schemas import (
    TwoFactorChallengeResponseSchema,
    TwoFactorConfirmRequestSchema,
    TwoFactorLoginConfirmResponseSchema,
)
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.users.models import User

router = APIRouter(
    prefix="/auth/2fa",
    tags=["Two-Factor Authentication"],
)


@router.post(
    "/login/confirm",
    response_model=TwoFactorLoginConfirmResponseSchema,
)
async def confirm_login(
    data: TwoFactorConfirmRequestSchema,
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    return await service.confirm_login(
        challenge_id=data.challenge_id,
        code=data.code,
    )


@router.post(
    "/enable",
    response_model=TwoFactorChallengeResponseSchema,
)
async def enable(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    return await service.request_enable(current_user)


@router.post(
    "/enable/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def confirm_enable(
    data: TwoFactorConfirmRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    await service.confirm_enable(
        current_user,
        data.challenge_id,
        data.code,
    )


@router.post(
    "/disable",
    response_model=TwoFactorChallengeResponseSchema,
)
async def disable(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    return await service.request_disable(current_user)


@router.post(
    "/disable/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def confirm_disable(
    data: TwoFactorConfirmRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[
        TwoFactorServiceInterface,
        Depends(get_two_factor_service),
    ],
):
    await service.confirm_disable(
        current_user,
        data.challenge_id,
        data.code,
    )
