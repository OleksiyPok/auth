# app/users/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.users.dependencies import get_user_service
from app.users.models import User
from app.users.schemas import (
    UserDetailedResponseSchema,
    UserResponseSchema,
    UserUpdateRequestSchema,
)
from app.users.service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    summary="Get all users",
    description="Get all registered users.",
    response_model=list[UserResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    service: Annotated[UserService, Depends(get_user_service)],
) -> list[User]:
    return await service.get_all()


@router.get(
    "/me",
    summary="Get current user",
    description="Get current authenticated user.",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@router.get(
    "/{user_id}",
    summary="Get a user",
    description="Get a registered user.",
    response_model=UserDetailedResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_by_id(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return await service.get_by_id(user_id)


@router.patch(
    "/me",
    summary="Update a user data",
    description="Update a user data.",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_self(
    data: UserUpdateRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> User:

    return await service.update_self(current_user, data)
