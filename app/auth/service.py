# app/auth/service.py

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

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
from app.sessions.exceptions import (
    InvalidRefreshTokenError,
    SessionExpiredError,
    SessionNotFoundError,
    SessionRevokedError,
)
from app.sessions.service import SessionService
from app.users.interfaces import UserRepositoryInterface
from app.users.models import User


class AuthService:

    def __init__(
        self,
        repository: UserRepositoryInterface,
        session_service: SessionService,
    ):
        self._repository = repository
        self._session_service = session_service

    async def register(
        self,
        data: RegisterRequestSchema,
    ) -> User:

        if await self._repository.get_by_login(data.login):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "USER_ALREADY_EXISTS",
                    "message": "User already exists",
                },
            )

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
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid login or password",
                },
            )

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid login or password",
                },
            )

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "USER_INACTIVE",
                    "message": "User is inactive",
                },
            )

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
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Invalid access token",
                },
            )

        user_id = payload.get("sub")
        session_id = payload.get("sid")

        if not user_id or not session_id:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Invalid token payload",
                },
            )

        try:
            session = await self._session_service.validate_session(
                session_id,
            )

        except SessionNotFoundError:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "SESSION_NOT_FOUND",
                    "message": "Session not found",
                },
            )

        except SessionRevokedError:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "SESSION_REVOKED",
                    "message": "Session revoked",
                },
            )

        except SessionExpiredError:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "SESSION_EXPIRED",
                    "message": "Session expired",
                },
            )

        user = await self._repository.get_by_id(
            user_id,
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found",
                },
            )

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "USER_INACTIVE",
                    "message": "User inactive",
                },
            )

        return user

    async def refresh(
        self,
        refresh_token: str,
    ) -> TokenResponseSchema:

        session = await self._session_service.validate_refresh_token(
            refresh_token,
        )

        try:
            session = await self._session_service.validate_refresh_token(
                refresh_token,
            )

        except InvalidRefreshTokenError:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Invalid refresh token",
                },
            )

        except SessionRevokedError:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "SESSION_REVOKED",
                    "message": "Session revoked",
                },
            )

        except SessionExpiredError:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "SESSION_EXPIRED",
                    "message": "Session expired",
                },
            )

        user = await self._repository.get_by_id(
            session.user_id,
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found",
                },
            )

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "USER_INACTIVE",
                    "message": "User is inactive",
                },
            )

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
