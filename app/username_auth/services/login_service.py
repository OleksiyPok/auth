# app/username_auth/services/login_service.py

from app.core.identifiers import normalize_username
from app.identities.types import IdentityType
from app.infrastructure.password import verify_password
from app.sessions.schemas import AuthenticationResponseSchema
from app.two_factor.services.service_interface import TwoFactorServiceInterface
from app.username_auth.exceptions import InvalidCredentialsError
from app.username_auth.repository.repository_interface import (
    UsernameIdentityRepositoryInterface,
)
from app.username_auth.schemas import LoginRequestSchema
from app.username_auth.services.login_service_interface import (
    UsernameLoginServiceInterface,
)
from app.users.exceptions import InactiveUserError, UserNotFoundError
from app.users.repository.repository_interface import UserRepositoryInterface


class UsernameLoginService(UsernameLoginServiceInterface):

    def __init__(
        self,
        local_identity_repository: UsernameIdentityRepositoryInterface,
        user_repository: UserRepositoryInterface,
        two_factor_service: TwoFactorServiceInterface,
    ):
        self._local_identity_repository = local_identity_repository
        self._user_repository = user_repository
        self._two_factor_service = two_factor_service

    async def login(
        self,
        data: LoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthenticationResponseSchema:

        username = normalize_username(data.username)

        identity = await self._local_identity_repository.get_by_username(username)

        if not identity:
            raise InvalidCredentialsError()

        if not verify_password(data.password, identity.password_hash):
            raise InvalidCredentialsError()

        user = await self._user_repository.get_by_id(identity.user_id)

        if not user:
            raise UserNotFoundError()

        if not user.is_active:
            raise InactiveUserError()

        return await self._two_factor_service.authenticate_or_challenge(
            user=user,
            identity_id=identity.id,
            identity_type=IdentityType.USERNAME,
            ip_address=ip_address,
            user_agent=user_agent,
        )
