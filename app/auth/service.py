# app/auth/service.py

from fastapi import HTTPException

from app.auth.schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    TokenResponseSchema,
)
from app.core.security import (
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.users.interfaces import UserRepositoryInterface
from app.users.models import User


class AuthService:

    def __init__(
        self,
        repository: UserRepositoryInterface,
    ):
        self._repository = repository

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

        return TokenResponseSchema(
            access_token=access_token,
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
