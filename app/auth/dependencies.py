# app/auth/dependencies.py

from fastapi import Depends

from app.auth.service import AuthService
from app.users.dependencies import get_user_repository
from app.users.interfaces import UserRepositoryInterface


def get_auth_service(
    repository: UserRepositoryInterface = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)
