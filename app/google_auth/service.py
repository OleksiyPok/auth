# app/google_auth/service.py

from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.google_auth.exceptions import GoogleOAuthStateError
from app.google_auth.models import GoogleIdentity, GoogleOAuthState
from app.google_auth.repository_interface import GoogleAuthRepositoryInterface
from app.google_auth.service_interface import GoogleAuthServiceInterface
from app.infrastructure.google.oauth import (
    exchange_google_code,
    get_google_authorization_url,
    get_google_user_info,
)
from app.infrastructure.jwt.refresh_token import generate_refresh_token
from app.infrastructure.jwt.security import create_access_token
from app.sessions.schemas import TokenResponseSchema
from app.sessions.services.service_interface import SessionServiceInterface
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface

OAUTH_STATE_EXPIRE_MINUTES = 10


class GoogleAuthService(GoogleAuthServiceInterface):

    def __init__(
        self,
        repository: GoogleAuthRepositoryInterface,
        user_repository: UserRepositoryInterface,
        session_service: SessionServiceInterface,
    ):
        self._repository = repository
        self._user_repository = user_repository
        self._session_service = session_service

    async def create_authorization_url(self) -> str:
        authorization_url, state, code_verifier = get_google_authorization_url()

        oauth_state = GoogleOAuthState(
            state=state,
            code_verifier=code_verifier,
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(minutes=OAUTH_STATE_EXPIRE_MINUTES)
            ),
        )

        await self._repository.create_oauth_state(oauth_state)

        return authorization_url

    async def handle_callback(
        self,
        code: str,
        state: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema:
        oauth_state = await self._repository.get_oauth_state(state)

        if oauth_state is None:
            raise GoogleOAuthStateError()

        if oauth_state.used:
            raise GoogleOAuthStateError()

        if oauth_state.expires_at <= datetime.now(timezone.utc):
            raise GoogleOAuthStateError()

        credentials = exchange_google_code(
            code=code,
            state=state,
            code_verifier=oauth_state.code_verifier,
        )

        google_user = get_google_user_info(credentials)

        await self._repository.mark_oauth_state_used(oauth_state)

        google_user_id = google_user["google_user_id"]

        existing_identity = await self._repository.get_identity_by_google_user_id(
            google_user_id,
        )

        if existing_identity is not None:
            user_id = existing_identity.user_id
        else:
            user = User(
                email=google_user["email"],
                first_name=google_user["first_name"],
                last_name=google_user["last_name"],
            )

            user = await self._user_repository.create(user)
            user_id = user.id

            identity = GoogleIdentity(
                user_id=user_id,
                google_user_id=google_user_id,
            )

            await self._repository.create_identity(identity)

        refresh_token = generate_refresh_token()

        session = await self._session_service.create_session(
            user_id=user_id,
            refresh_token=refresh_token,
            provider="google",
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
            },
        )

        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
