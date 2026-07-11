# app/users/router.py

from fastapi import APIRouter, Depends, status

from app.users.dependencies import get_user_service
from app.users.schemas import DeleteUserResponseSchema, UserResponseSchema
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
