# app/sessions/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.auth.rbac.dependencies import (
    require_self_sessions_read,
    require_self_sessions_revoke,
)
from app.sessions.dependencies import get_sessions_service
from app.sessions.exceptions import SessionAccessDeniedError, SessionNotFoundError
from app.sessions.schemas import SessionResponseSchema
from app.sessions.service_interface import SessionServiceInterface
from app.users.models import User

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.get(
    "",
    response_model=list[SessionResponseSchema],
    dependencies=[Depends(require_self_sessions_read())],
)
async def get_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    service: SessionServiceInterface = Depends(get_sessions_service),
):
    sessions = await service.get_user_sessions(
        current_user.id,
    )

    return [SessionResponseSchema.model_validate(session) for session in sessions]


@router.post(
    "/revoke_all_session",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_self_sessions_revoke())],
)
async def revoke_all_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SessionServiceInterface, Depends(get_sessions_service)],
):
    await service.revoke_all_sessions(
        current_user,
    )


@router.post(
    "/{session_id}/revoke",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_self_sessions_revoke())],
)
async def revoke_session(
    session_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SessionServiceInterface, Depends(get_sessions_service)],
):
    session = await service.get_by_id(
        session_id,
    )

    if not session:
        raise SessionNotFoundError()

    if session.user_id != current_user.id:
        raise SessionAccessDeniedError()

    await service.revoke_session(
        session_id,
    )
