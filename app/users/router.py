# app/users/router.py

from fastapi import APIRouter, Depends, status

from app.users.dependencies import get_user_service
from app.users.schemas import UserResponseSchema
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
async def get_users(
    service: UserService = Depends(get_user_service),
):
    return await service.get_all()
