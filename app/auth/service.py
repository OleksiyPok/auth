# app/auth/service.py

from datetime import timedelta

from fastapi import HTTPException

from app.auth.schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    TokenResponseSchema,
)
from app.core.config import settings
from app.core.security import (
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.sessions.schemas import SessionResponseSchema
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

        access_token = create_access_token(
            subject=user.id,
        )

        refresh_token = self._session_service.generate_refresh_token()

        await self._session_service.create_session(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            ip_address=ip_address,
            user_agent=user_agent,
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

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Invalid token payload",
                },
            )

        user = await self._repository.get_by_id(user_id)

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

        return user

    async def refresh(
        self,
        refresh_token: str,
    ) -> TokenResponseSchema:

        session = await self._session_service.validate_refresh_token(
            refresh_token,
        )

        if not session:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Invalid refresh token",
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
        )

        new_refresh_token = self._session_service.generate_refresh_token()

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

    async def logout_all(
        self,
        user: User,
    ) -> None:

        await self._session_service.deactivate_user_sessions(
            user.id,
        )

    async def get_sessions(
        self,
        user: User,
    ) -> list[SessionResponseSchema]:

        sessions = await self._session_service.get_active_user_sessions(
            user.id,
        )

        return [SessionResponseSchema.model_validate(session) for session in sessions]
