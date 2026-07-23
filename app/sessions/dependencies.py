# app/sessions/dependencies.py

from fastapi import Depends

from app.db.session import get_session
from app.sessions.interfaces import SessionRepositoryInterface
from app.sessions.repository import SessionRepository
from app.sessions.service import SessionService


def get_session_repository(
    session=Depends(get_session),
) -> SessionRepositoryInterface:
    return SessionRepository(session)


def get_session_service(
    repository: SessionRepositoryInterface = Depends(get_session_repository),
) -> SessionService:
    return SessionService(repository)
