# app/two_factor/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user, require_fresh_session
from app.core.rate_limit import CONFIRM_IP, SEND_CODE_IP, UNLINK_IP, limit_by_ip
from app.two_factor.dependencies import get_two_factor_service
from app.two_factor.schemas import (
    TwoFactorAddEmailMethodRequestSchema,
    TwoFactorChallengeResponseSchema,
    TwoFactorConfirmRequestSchema,
    TwoFactorLoginConfirmResponseSchema,
    TwoFactorRecoveryCodesResponseSchema,
    TwoFactorResendRequestSchema,
    TwoFactorStatusResponseSchema,
)
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.users.models import User

router = APIRouter(
    prefix="/auth/2fa",
)


@router.get(
    "/status",
    tags=["Two-Factor Settings"],
    response_model=TwoFactorStatusResponseSchema,
)
async def get_status(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    return TwoFactorStatusResponseSchema(
        enabled=await service.is_enabled(current_user.id),
        methods=await service.get_methods(current_user.id),
    )


@router.post(
    "/methods/email",
    tags=["Two-Factor Settings"],
    response_model=TwoFactorChallengeResponseSchema,
    dependencies=[
        Depends(limit_by_ip(SEND_CODE_IP)),
        Depends(require_fresh_session),
    ],
)
async def add_email_method(
    data: TwoFactorAddEmailMethodRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    return await service.request_add_email_method(current_user, data.email)


@router.post(
    "/methods/email/confirm",
    tags=["Two-Factor Settings"],
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(limit_by_ip(CONFIRM_IP))],
)
async def confirm_add_email_method(
    data: TwoFactorConfirmRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    await service.confirm_add_email_method(
        current_user,
        data.challenge_id,
        data.code,
    )


@router.delete(
    "/methods/{method_id}",
    tags=["Two-Factor Settings"],
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(limit_by_ip(UNLINK_IP)),
        Depends(require_fresh_session),
    ],
)
async def remove_method(
    method_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    await service.remove_method(current_user, method_id)


@router.post(
    "/recovery-codes",
    tags=["Two-Factor Settings"],
    response_model=TwoFactorRecoveryCodesResponseSchema,
    dependencies=[Depends(limit_by_ip(SEND_CODE_IP))],
)
async def generate_recovery_codes(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    return TwoFactorRecoveryCodesResponseSchema(
        codes=await service.generate_recovery_codes(current_user)
    )


@router.post(
    "/login/confirm",
    tags=["Two-Factor Login"],
    response_model=TwoFactorLoginConfirmResponseSchema,
    dependencies=[Depends(limit_by_ip(CONFIRM_IP))],
)
async def confirm_login(
    data: TwoFactorConfirmRequestSchema,
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    return await service.confirm_login(
        challenge_id=data.challenge_id,
        code=data.code,
    )


@router.post(
    "/login/resend",
    tags=["Two-Factor Login"],
    response_model=TwoFactorChallengeResponseSchema,
    dependencies=[Depends(limit_by_ip(SEND_CODE_IP))],
)
async def resend_login_code(
    data: TwoFactorResendRequestSchema,
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    return await service.resend_login_code(data.challenge_id)


@router.post(
    "/enable",
    tags=["Two-Factor Settings"],
    response_model=TwoFactorChallengeResponseSchema,
    dependencies=[Depends(limit_by_ip(SEND_CODE_IP))],
)
async def enable(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    return await service.request_enable(current_user)


@router.post(
    "/enable/confirm",
    tags=["Two-Factor Settings"],
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(limit_by_ip(CONFIRM_IP))],
)
async def confirm_enable(
    data: TwoFactorConfirmRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    await service.confirm_enable(current_user, data.challenge_id, data.code)


@router.post(
    "/disable",
    tags=["Two-Factor Settings"],
    response_model=TwoFactorChallengeResponseSchema,
    dependencies=[
        Depends(limit_by_ip(SEND_CODE_IP)),
        Depends(require_fresh_session),
    ],
)
async def disable(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    return await service.request_disable(current_user)


@router.post(
    "/disable/confirm",
    tags=["Two-Factor Settings"],
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(limit_by_ip(CONFIRM_IP))],
)
async def confirm_disable(
    data: TwoFactorConfirmRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TwoFactorServiceInterface, Depends(get_two_factor_service)],
):
    await service.confirm_disable(current_user, data.challenge_id, data.code)
