# app/google_auth/services/service.py

from datetime import datetime, timedelta, timezone

from app.google_auth.exceptions import (
    GoogleEmailNotVerifiedError,
    GoogleOAuthStateError,
)
from app.google_auth.models import GoogleIdentity, GoogleOAuthState
from app.google_auth.purpose import GoogleOAuthPurpose
from app.google_auth.repository.repository_interface import (
    GoogleAuthRepositoryInterface,
)
from app.google_auth.schemas import GoogleCallbackResponse, GoogleLinkResponseSchema
from app.google_auth.services.service_interface import GoogleAuthServiceInterface
from app.identities.exceptions import IdentityConflictError, IdentityTypeConflictError
from app.identities.types import IdentityType
from app.infrastructure.google.oauth import (
    exchange_google_code,
    get_google_authorization_url,
    get_google_user_info,
)
from app.merge.exceptions import MergeAccountNotFoundError
from app.merge.schemas import MergeProofResponseSchema
from app.merge.services.proof_service_interface import MergeProofServiceInterface
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.users.exceptions import InactiveUserError
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface

OAUTH_STATE_EXPIRE_MINUTES = 10


class GoogleAuthService(GoogleAuthServiceInterface):

    def __init__(
        self,
        repository: GoogleAuthRepositoryInterface,
        user_repository: UserRepositoryInterface,
        two_factor_service: TwoFactorServiceInterface,
        merge_proof_service: MergeProofServiceInterface,
    ):
        self._repository = repository
        self._user_repository = user_repository
        self._two_factor_service = two_factor_service
        self._merge_proof_service = merge_proof_service

    async def create_authorization_url(
        self,
        purpose: GoogleOAuthPurpose = GoogleOAuthPurpose.LOGIN,
        user_id: str | None = None,
    ) -> str:
        authorization_url, state, code_verifier = get_google_authorization_url()

        oauth_state = GoogleOAuthState(
            state=state,
            code_verifier=code_verifier,
            purpose=purpose,
            user_id=user_id,
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
    ) -> GoogleCallbackResponse:
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

        if not google_user["email_verified"]:
            raise GoogleEmailNotVerifiedError()

        await self._repository.mark_oauth_state_used(oauth_state)

        google_user_id = google_user["google_user_id"]

        if oauth_state.purpose == GoogleOAuthPurpose.LINK:
            return await self._link_google(oauth_state, google_user_id)

        if oauth_state.purpose == GoogleOAuthPurpose.MERGE:
            return await self._create_merge_proof(oauth_state, google_user_id)

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

        user = await self._user_repository.get_by_id(
            identity.user_id,
        )

        if user is None:
            raise GoogleOAuthStateError("Google user not found")

        if not user.is_active:
            raise InactiveUserError()

        return await self._two_factor_service.authenticate_or_challenge(
            user=user,
            identity_id=identity.id,
            identity_type=IdentityType.GOOGLE,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def _link_google(
        self,
        oauth_state: GoogleOAuthState,
        google_user_id: str,
    ) -> GoogleLinkResponseSchema:
        """Add the Google account to the user who started the link.

        No tokens are issued: the user is already signed in.
        """
        if oauth_state.user_id is None:
            raise GoogleOAuthStateError()

        user = await self._user_repository.get_by_id(oauth_state.user_id)

        if user is None:
            raise GoogleOAuthStateError("Google user not found")

        if not user.is_active:
            raise InactiveUserError()

        if await self._repository.get_identity_by_user_id(user.id) is not None:
            raise IdentityTypeConflictError()

        if (
            await self._repository.get_identity_by_google_user_id(google_user_id)
            is not None
        ):
            raise IdentityConflictError()

        identity = await self._repository.create_identity(
            GoogleIdentity(
                user_id=user.id,
                google_user_id=google_user_id,
            )
        )

        return GoogleLinkResponseSchema(identity_id=identity.id)

    async def _create_merge_proof(
        self,
        oauth_state: GoogleOAuthState,
        google_user_id: str,
    ) -> MergeProofResponseSchema:
        """Prove the Google account of another user for a merge.

        The user who started the flow is the target of the merge; the owner of
        the Google account is the source. No tokens are issued.
        """
        if oauth_state.user_id is None:
            raise GoogleOAuthStateError()

        target_user = await self._user_repository.get_by_id(oauth_state.user_id)

        if target_user is None:
            raise GoogleOAuthStateError("Google user not found")

        identity = await self._repository.get_identity_by_google_user_id(
            google_user_id,
        )

        if identity is None:
            raise MergeAccountNotFoundError()

        return await self._merge_proof_service.create_for_source(
            target_user,
            identity.user_id,
        )
