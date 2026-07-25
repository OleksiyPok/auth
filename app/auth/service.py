# app/auth/service.py

from datetime import timedelta

from app.auth.exceptions import (
    AuthenticatedUserNotFoundError,
    InvalidCredentialsError,
    InvalidTokenError,
    InvalidTokenPayloadError,
    SessionNotFoundAuthError,
    UserAlreadyExistsError,
    UserInactiveError,
)
from app.auth.schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    TokenResponseSchema,
)
from app.core.config import settings
from app.core.refresh_token import generate_refresh_token
from app.core.security import (
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.sessions.exceptions import SessionNotFoundError
from app.sessions.interfaces import SessionServiceInterface
from app.users.interfaces import UserRepositoryInterface
from app.users.models import User


class AuthService:

    def __init__(
        self,
        repository: UserRepositoryInterface,
        session_service: SessionServiceInterface,
    ):
        self._repository = repository
        self._session_service = session_service

    async def register(
        self,
        data: RegisterRequestSchema,
    ) -> User:

        if await self._repository.get_by_login(data.login):
            raise UserAlreadyExistsError()

        user = User(
            login=data.login,
            password_hash=hash_password(data.password),
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )

        return await self._repository.create(user)

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
            raise UserInactiveError()

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

    async def authenticate_token(
        self,
        token: str,
    ) -> User:

        try:
            payload = decode_access_token(token)

        except InvalidAccessTokenError:
            raise InvalidTokenError()

        user_id = payload.get("sub")
        session_id = payload.get("sid")

        if not user_id or not session_id:
            raise InvalidTokenPayloadError()

        try:
            await self._session_service.validate_session(
                session_id,
            )

        except SessionNotFoundError:
            raise SessionNotFoundAuthError()

        user = await self._repository.get_by_id(
            user_id,
        )

        if not user:
            raise AuthenticatedUserNotFoundError()

        if not user.is_active:
            raise UserInactiveError()

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
            raise AuthenticatedUserNotFoundError()

        if not user.is_active:
            raise UserInactiveError()

        new_access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "sid": session.id,
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

    async def logout(
        self,
        refresh_token: str,
    ) -> None:

        session = await self._session_service.get_by_refresh_token(
            refresh_token,
        )

        if session:
            await self._session_service.revoke(session)
