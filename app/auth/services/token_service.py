# app/auth/services/token_service.py

from app.auth.exceptions import InvalidAccessTokenError
from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.auth.services.token_service_interface import TokenServiceInterface
from app.identities.services.service_interface import IdentityServiceInterface
from app.infrastructure.jwt.security import (
    InvalidAccessTokenError as SecurityInvalidAccessTokenError,
)
from app.infrastructure.jwt.security import decode_access_token
from app.sessions.exceptions import SessionRevokedError
from app.sessions.models import Session
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
        identity_service: IdentityServiceInterface,
    ):
        self._repository = repository
        self._session_service = session_service
        self._auth_session_service = auth_session_service
        self._identity_service = identity_service

    async def _ensure_identity_owned(
        self,
        session: Session,
    ) -> None:
        # Session.identity_id has no foreign key (it points to one of three
        # tables), so ownership is checked here: the identity must still exist
        # and belong to the session's user. This stops the sessions of an
        # identity that was unlinked, merged or split away, even if they were
        # not revoked.
        owner_id = await self._identity_service.get_owner_id(
            session.identity_type,
            session.identity_id,
        )

        if owner_id != session.user_id:
            raise SessionRevokedError()

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
        identity_id = payload.get("identity_id")

        if not user_id or not session_id or not identity_id:
            raise InvalidAccessTokenError()

        session = await self._session_service.validate_session(
            session_id,
        )

        if session.user_id != user_id:
            raise InvalidAccessTokenError()

        if session.identity_id != identity_id:
            raise InvalidAccessTokenError()

        await self._ensure_identity_owned(session)

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

        await self._ensure_identity_owned(session)

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
