# app/local_auth/services/login_service.py

from app.auth.services.auth_session_service_interface import AuthSessionServiceInterface
from app.infrastructure.password import verify_password
from app.local_auth.exceptions import InvalidCredentialsError
from app.local_auth.repository.repository_interface import (
    LocalIdentityRepositoryInterface,
)
from app.local_auth.schemas import LoginRequestSchema
from app.local_auth.services.login_service_interface import LocalLoginServiceInterface
from app.sessions.schemas import TokenResponseSchema
from app.users.exceptions import UserNotFoundError
from app.users.repository.repository_interface import UserRepositoryInterface


class LocalLoginService(LocalLoginServiceInterface):

    def __init__(
        self,
        local_identity_repository: LocalIdentityRepositoryInterface,
        user_repository: UserRepositoryInterface,
        auth_session_service: AuthSessionServiceInterface,
    ):
        self._local_identity_repository = local_identity_repository
        self._user_repository = user_repository
        self._auth_session_service = auth_session_service

    async def login(
        self,
        data: LoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema:

        identity = await self._local_identity_repository.get_by_login(
            data.login,
        )

        if not identity:
            raise InvalidCredentialsError()

        if not verify_password(
            data.password,
            identity.password_hash,
        ):
            raise InvalidCredentialsError()

        user = await self._user_repository.get_by_id(
            identity.user_id,
        )

        if not user:
            raise UserNotFoundError()

        return await self._auth_session_service.create_tokens(
            user_id=user.id,
            provider="local",
            ip_address=ip_address,
            user_agent=user_agent,
        )
