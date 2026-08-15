# app/auth/services/token_service.py

from app.auth.exceptions import InvalidAccessTokenError
from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.auth.services.token_service_interface import TokenServiceInterface
from app.infrastructure.jwt.security import (
    InvalidAccessTokenError as SecurityInvalidAccessTokenError,
)
from app.infrastructure.jwt.security import decode_access_token
from app.sessions.schemas import TokenResponseSchema
from app.sessions.services.service_interface import SessionServiceInterface
from app.users.exceptions import InactiveUserError, UserNotFoundError
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface


class TokenService(TokenServiceInterface):

    def __init__(
        self,
        repository: UserRepositoryInterface,
        session_service: SessionServiceInterface,
        auth_session_service: AuthSessionServiceInterface,
    ):
        self._repository = repository
        self._session_service = session_service
        self._auth_session_service = auth_session_service

    async def authenticate(
        self,
        token: str,
    ) -> User:

        try:
            payload = decode_access_token(token)

        except SecurityInvalidAccessTokenError as exc:
            raise InvalidAccessTokenError(str(exc)) from exc

        user_id = payload.get("sub")
        session_id = payload.get("sid")

        if not user_id or not session_id:
            raise InvalidAccessTokenError()

        await self._session_service.validate_session(
            session_id,
        )

        user = await self._repository.get_by_id(
            user_id,
        )

        if not user:
            raise UserNotFoundError()

        if not user.is_active:
            raise InactiveUserError()

        return user

    async def refresh(
        self,
        refresh_token: str,
    ) -> TokenResponseSchema:

        session = await self._session_service.validate_refresh_token(
            refresh_token,
        )

        user = await self._repository.get_by_id(
            session.user_id,
        )

        if not user:
            raise UserNotFoundError()

        if not user.is_active:
            raise InactiveUserError()

        return await self._auth_session_service.refresh_tokens(
            session,
        )
