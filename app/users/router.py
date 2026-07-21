# app/users/router.py

from fastapi import APIRouter, Depends, status

from app.users.dependencies import get_user_service
from app.users.schemas import UserResponseSchema, UserUpdateRequestSchema
from app.users.service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/",
    summary="Get all users",
    description="Get all registered users.",
    response_model=list[UserResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    service: UserService = Depends(get_user_service),
):
    return await service.get_all()


@router.get(
    "/{user_id}",
    summary="Get a user",
    description="Get a registered user.",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_by_id(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
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
    # current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    current_user = await service.get_by_login("test")
    return await service.update_self(current_user, data)


# @router.patch(
#     "/{user_id}",
#     summary="Update a user",
#     description="Update a registered user.",
#     response_model=UserResponseSchema,
#     status_code=status.HTTP_200_OK,
# )
# async def update(
#     user_id: str,
#     data: UserRequestSuperadminSchema,
#     service: UserService = Depends(get_user_service),
# ):
#     return await service.update(user_id, data)


@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="Delete a user.",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
)
async def delete(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    return await service.delete(user_id)
