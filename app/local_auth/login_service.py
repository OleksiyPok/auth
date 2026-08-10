# app/local_auth/login_service.py

from datetime import timedelta

from app.auth.exceptions import InvalidCredentialsError
from app.auth.schemas import TokenResponseSchema
from app.core.config import settings
from app.infrastructure.jwt.refresh_token import generate_refresh_token
from app.infrastructure.jwt.security import create_access_token
from app.infrastructure.password import verify_password
from app.local_auth.login_service_interface import LocalLoginServiceInterface
from app.local_auth.schemas import LoginRequestSchema
from app.local_auth.service_interface import LocalAuthServiceInterface
from app.sessions.service_interface import SessionServiceInterface
from app.users.exceptions import UserNotFoundError
from app.users.repository_interface import UserRepositoryInterface


class LocalLoginService(LocalLoginServiceInterface):

    def __init__(
        self,
        local_auth_service: LocalAuthServiceInterface,
        user_repository: UserRepositoryInterface,
        session_service: SessionServiceInterface,
    ):
        self._local_auth_service = local_auth_service
        self._user_repository = user_repository
        self._session_service = session_service

    async def login(
        self,
        data: LoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema:

        identity = await self._local_auth_service.get_by_login(
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

        refresh_token = generate_refresh_token()

        session = await self._session_service.create_session(
            user_id=user.id,
            refresh_token=refresh_token,
            provider="local",
            expires_delta=timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
            ),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "sid": session.id,
            },
        )

        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
