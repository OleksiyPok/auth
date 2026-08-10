# app/local_auth/dependencies.py

from typing import Annotated

from fastapi import Depends

from app.db.session import get_session
from app.local_auth.repository import LocalIdentityRepository
from app.local_auth.repository_interface import LocalIdentityRepositoryInterface
from app.local_auth.service import LocalAuthService
from app.local_auth.service_interface import LocalAuthServiceInterface


async def get_local_identity_repository(
    session=Depends(get_session),
) -> LocalIdentityRepositoryInterface:
    return LocalIdentityRepository(session)


async def get_local_auth_service(
    repository: Annotated[
        LocalIdentityRepositoryInterface,
        Depends(get_local_identity_repository),
    ],
) -> LocalAuthServiceInterface:
    return LocalAuthService(repository)
