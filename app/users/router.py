# app/users/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.auth.rbac.dependencies import (
    require_role_management,
    require_self_deactivate,
    require_self_read,
    require_self_write,
    require_users_deactivate,
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
from app.users.services.service_interface import UserServiceInterface

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
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
) -> list[UserResponseSchema]:
    users = await service.get_all()

    return [
        UserResponseSchema(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )
        for user in users
    ]


@router.get(
    "/me",
    summary="Get current user",
    description="Get current authenticated user.",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_self_read())],
)
async def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> UserResponseSchema:
    return UserResponseSchema(
        id=current_user.id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
    )


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
    service: Annotated[
        UserServiceInterface,
        Depends(get_user_service),
    ],
) -> UserDetailedResponseSchema:
    user = await service.get_by_id(user_id)

    return UserDetailedResponseSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


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
    service: Annotated[
        UserServiceInterface,
        Depends(get_user_service),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> UserResponseSchema:
    user = await service.update_self(
        current_user,
        data,
    )

    return UserResponseSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )


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
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponseSchema:
    user = await service.change_role(
        user_id,
        role_data,
        current_user.id,
    )

    return UserResponseSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )


@router.post(
    "/me/deactivate",
    summary="Deactivate current user",
    description="Deactivate the account of the current user.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_self_deactivate())],
)
async def deactivate_me(
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await service.deactivate_user(
        current_user=current_user,
        target_user=current_user,
    )


@router.post(
    "/{user_id}/deactivate",
    summary="Deactivate a user",
    description="Deactivate another user. Requires the permission to deactivate users.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_users_deactivate())],
)
async def deactivate_user(
    user_id: str,
    service: Annotated[
        UserServiceInterface,
        Depends(get_user_service),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> None:
    target_user = await service.get_user(user_id)

    await service.deactivate_user(
        current_user=current_user,
        target_user=target_user,
    )