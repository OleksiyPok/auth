# app/auth/services/login_service.py

from datetime import timedelta

from app.auth.exceptions import InvalidCredentialsError
from app.auth.schemas import LoginRequestSchema, TokenResponseSchema
from app.auth.services.login_service_interface import LoginServiceInterface
from app.core.config import settings
from app.infrastructure.jwt.refresh_token import generate_refresh_token
from app.infrastructure.jwt.security import create_access_token
from app.infrastructure.password import verify_password
from app.sessions.service_interface import SessionServiceInterface
from app.users.exceptions import InactiveUserError
from app.users.repository_interface import UserRepositoryInterface


class LoginService(LoginServiceInterface):
    def __init__(
        self,
        repository: UserRepositoryInterface,
        session_service: SessionServiceInterface,
    ):
        self._repository = repository
        self._session_service = session_service

    async def login(
        self,
        data: LoginRequestSchema,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponseSchema:

        user = await self._repository.get_by_login(data.login)

        if not user:
            raise InvalidCredentialsError()

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        refresh_token = generate_refresh_token()

        session = await self._session_service.create_session(
            user_id=user.id,
            refresh_token=refresh_token,
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

    async def logout(
        self,
        refresh_token: str,
    ) -> None:

        session = await self._session_service.get_by_refresh_token(
            refresh_token,
        )

        if session:
            await self._session_service.revoke(session)
