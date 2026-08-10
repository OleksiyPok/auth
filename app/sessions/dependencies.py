# app/sessions/dependencies.py

from fastapi import Depends

from app.db.session import get_session
from app.sessions.repository.repository import SessionRepository
from app.sessions.repository.repository_interface import SessionRepositoryInterface
from app.sessions.services.service import SessionService
from app.sessions.services.service_interface import SessionServiceInterface


def get_session_repository(
    session=Depends(get_session),
) -> SessionRepositoryInterface:
    return SessionRepository(session)


def get_sessions_service(
    repository: SessionRepositoryInterface = Depends(get_session_repository),
) -> SessionServiceInterface:
    return SessionService(repository)
