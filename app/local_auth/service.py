# app/local_auth/service.py

from app.local_auth.models import LocalIdentity
from app.local_auth.repository_interface import LocalIdentityRepositoryInterface
from app.local_auth.service_interface import LocalAuthServiceInterface


class LocalAuthService(LocalAuthServiceInterface):

    def __init__(
        self,
        repository: LocalIdentityRepositoryInterface,
    ):
        self._repository = repository

    async def get_by_user_id(
        self,
        user_id: str,
    ) -> LocalIdentity | None:
        return await self._repository.get_by_user_id(user_id)

    async def get_by_login(
        self,
        login: str,
    ) -> LocalIdentity | None:
        return await self._repository.get_by_login(login)
