# app/sessions/router.py

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_auth_service, get_current_user
from app.auth.service import AuthService
from app.sessions.schemas import SessionResponseSchema
from app.users.models import User

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.get(
    "",
    response_model=list[SessionResponseSchema],
)
async def get_sessions(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    return await service.get_sessions(
        current_user,
    )


@router.post(
    "/revoke_all_session",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_all_session(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    await service.revoke_all_session(
        current_user,
    )


@router.post(
    "/{session_id}/revoke",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    await service.revoke_session(
        current_user,
        session_id,
    )
