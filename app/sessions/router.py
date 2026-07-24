# app/sessions/router.py

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.sessions.dependencies import get_sessions_service
from app.sessions.schemas import SessionResponseSchema
from app.sessions.service import SessionService
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
    service: SessionService = Depends(get_sessions_service),
):
    sessions = await service.get_user_sessions(
        current_user.id,
    )

    return [SessionResponseSchema.model_validate(session) for session in sessions]


@router.post(
    "/revoke_all_session",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_all_session(
    current_user: User = Depends(get_current_user),
    service: SessionService = Depends(get_sessions_service),
):
    await service.revoke_all_sessions(
        current_user,
    )


@router.post(
    "/{session_id}/revoke",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    service: SessionService = Depends(get_sessions_service),
):
    session = await service.get_by_id(
        session_id,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found",
            },
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ACCESS_DENIED",
                "message": "Access denied",
            },
        )

    await service.revoke_session(
        session_id,
    )
