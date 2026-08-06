# app/users/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.auth.rbac.dependencies import (
    require_role_management,
    require_self_delete,
    require_self_read,
    require_self_write,
    require_users_delete,
    require_users_read,
)
from app.users.dependencies import get_user_service
from app.users.models import User
from app.users.schemas import (
    UserDetailedResponseSchema,
    UserResponseSchema,
    UserRoleAssignRequestSchema,
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
    dependencies=[Depends(require_users_read())],
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
    dependencies=[Depends(require_self_read())],
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
    dependencies=[Depends(require_users_read())],
)
async def get_by_id(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return await service.get_by_id(user_id)


@router.patch(
    "/me",
    summary="Update a user data",
    description="Update a user data.",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_self_write())],
)
async def update_self(
    data: UserUpdateRequestSchema,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:

    return await service.update_self(current_user, data)


@router.patch(
    "/{user_id}/role",
    summary="Assign a role to a user",
    description="Assign an existing role to another user. Requires admin privileges.",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role_management())],
)
async def assign_role(
    user_id: str,
    role_data: UserRoleAssignRequestSchema,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:

    return await service.change_role(user_id, role_data, current_user.id)


@router.delete(
    "/me",
    dependencies=[Depends(require_self_delete())],
)
async def deactivate_me(
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.deactivate_user(
        current_user=current_user,
        target_user=current_user,
    )


@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_users_delete())],
)
async def deactivate_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    target_user = await service.get_by_id(user_id)

    return await service.deactivate_user(
        current_user=current_user,
        target_user=target_user,
    )
