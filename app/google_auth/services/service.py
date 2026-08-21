# app/google_auth/services/service.py

from datetime import datetime, timedelta, timezone

from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.google_auth.exceptions import GoogleOAuthStateError
from app.google_auth.models import GoogleIdentity, GoogleOAuthState
from app.google_auth.repository.repository_interface import (
    GoogleAuthRepositoryInterface,
)
from app.google_auth.services.service_interface import GoogleAuthServiceInterface
from app.infrastructure.google.oauth import (
    exchange_google_code,
    get_google_authorization_url,
    get_google_user_info,
)
from app.sessions.schemas import AuthenticationResponseSchema
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface

OAUTH_STATE_EXPIRE_MINUTES = 10


class GoogleAuthService(GoogleAuthServiceInterface):

    def __init__(
        self,
        repository: GoogleAuthRepositoryInterface,
        user_repository: UserRepositoryInterface,
        auth_session_service: AuthSessionServiceInterface,
    ):
        self._repository = repository
        self._user_repository = user_repository
        self._auth_session_service = auth_session_service

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
    ) -> AuthenticationResponseSchema:
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

        identity = await self._repository.get_identity_by_google_user_id(
            google_user_id,
        )

        if identity is None:
            user = await self._user_repository.create(
                User(
                    first_name=google_user["first_name"],
                    last_name=google_user["last_name"],
                )
            )

            identity = await self._repository.create_identity(
                GoogleIdentity(
                    user_id=user.id,
                    google_user_id=google_user_id,
                )
            )

            await self._user_repository.commit()

        user = await self._user_repository.get_by_id(
            identity.user_id,
        )

        if user is None:
            raise GoogleOAuthStateError("Google user not found")

        tokens = await self._auth_session_service.create_tokens(
            user_id=user.id,
            identity_id=identity.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return AuthenticationResponseSchema(
            **tokens.model_dump(),
            requires_two_factor=False,
        )
