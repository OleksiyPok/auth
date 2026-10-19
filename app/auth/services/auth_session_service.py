# app/auth/services/auth_session_service.py

from datetime import timedelta

from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.core.config import settings
from app.infrastructure.jwt.refresh_token import generate_refresh_token
from app.infrastructure.jwt.security import create_access_token
from app.sessions.models import Session
from app.sessions.schemas import TokenResponseSchema
from app.sessions.services.service_interface import SessionServiceInterface


class AuthSessionService(AuthSessionServiceInterface):

    def __init__(
        self,
        session_service: SessionServiceInterface,
    ):
        self._session_service = session_service

    async def create_tokens(
        self,
        user_id: str,
        identity_id: str,
        identity_type: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema:
        refresh_token = generate_refresh_token()

        session = await self._session_service.create_session(
            user_id=user_id,
            identity_id=identity_id,
            identity_type=identity_type,
            refresh_token=refresh_token,
            expires_delta=timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
            ),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        access_token = create_access_token(
            subject=user_id,
            additional_claims={
                "sid": session.id,
                "identity_id": identity_id,
            },
        )

        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_tokens(
        self,
        session: Session,
    ) -> TokenResponseSchema:

        new_access_token = create_access_token(
            subject=session.user_id,
            additional_claims={
                "sid": session.id,
                "identity_id": session.identity_id,
            },
        )

        new_refresh_token = generate_refresh_token()

        await self._session_service.rotate_refresh_token(
            session=session,
            new_refresh_token=new_refresh_token,
            expires_delta=timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
            ),
        )

        return TokenResponseSchema(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )
