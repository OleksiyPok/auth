# app/users/services/service.py

from app.auth.rbac.role_permissions import validate_role
from app.auth.rbac.roles import Role
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.google_auth.repository.repository_interface import (
    GoogleAuthRepositoryInterface,
)
from app.sessions.repository.repository_interface import SessionRepositoryInterface
from app.sessions.services.service_interface import SessionServiceInterface
from app.two_factor.repository.repository_interface import TwoFactorRepositoryInterface
from app.username_auth.repository.repository_interface import (
    UsernameIdentityRepositoryInterface,
)
from app.users.exceptions import (
    CannotChangeOwnRoleError,
    CannotPurgeActiveUserError,
    LastSuperadminDeactivationError,
    UserAlreadyDeactivatedError,
    UserNotFoundError,
)
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface
from app.users.schemas import UserRoleAssignRequestSchema, UserUpdateRequestSchema
from app.users.services.service_interface import UserServiceInterface
from app.users.status import UserStatus


class UserService(UserServiceInterface):

    def __init__(
        self,
        repository: UserRepositoryInterface,
        session_service: SessionServiceInterface,
        session_repository: SessionRepositoryInterface,
        two_factor_repository: TwoFactorRepositoryInterface,
        username_identity_repository: UsernameIdentityRepositoryInterface,
        email_identity_repository: EmailIdentityRepositoryInterface,
        google_auth_repository: GoogleAuthRepositoryInterface,
    ):
        self._repository = repository
        self._session_service = session_service
        self._session_repository = session_repository
        self._two_factor_repository = two_factor_repository
        self._username_identity_repository = username_identity_repository
        self._email_identity_repository = email_identity_repository
        self._google_auth_repository = google_auth_repository

    async def get_user(
        self,
        user_id: str,
    ) -> User:
        user = await self._repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        return user

    async def get_by_id(
        self,
        user_id: str,
    ) -> User:
        return await self.get_user(user_id)

    async def get_all(self) -> list[User]:
        return await self._repository.get_all()

    async def update_self(
        self,
        user: User,
        data: UserUpdateRequestSchema,
    ) -> User:
        return await self._update(
            user,
            data,
        )

    async def delete(
        self,
        user_id: str,
    ) -> User:
        user = await self.get_user(user_id)

        return await self._repository.delete(user)

    async def change_role(
        self,
        user_id: str,
        role_data: UserRoleAssignRequestSchema,
        current_user_id: str,
    ) -> User:
        user = await self.get_user(user_id)

        validated_role = validate_role(role_data.role)

        if current_user_id == user.id:
            raise CannotChangeOwnRoleError()

        user.role = validated_role

        return await self._repository.update(user)

    async def deactivate_user(
        self,
        current_user: User,
        target_user: User,
        status: UserStatus,
    ) -> User:
        if status == UserStatus.ACTIVE:
            raise ValueError("A deactivated user needs a deactivated_* status")

        if not target_user.is_active:
            raise UserAlreadyDeactivatedError()

        if target_user.role == Role.SUPERADMIN:
            count = await self._repository.count_active_superadmins()

            if count == 1:
                raise LastSuperadminDeactivationError()

        user = await self._repository.deactivate(target_user, status)

        await self._session_service.revoke_all_sessions(user)

        return user

    async def purge_user(
        self,
        user: User,
    ) -> None:
        if user.is_active:
            raise CannotPurgeActiveUserError()

        await self._session_repository.delete_by_user_id(user.id)
        await self._two_factor_repository.delete_by_user_id(user.id)
        await self._username_identity_repository.delete_by_user_id(user.id)
        await self._email_identity_repository.delete_by_user_id(user.id)
        await self._google_auth_repository.delete_by_user_id(user.id)

        await self._repository.delete(user)

    async def _update(
        self,
        user: User,
        data: UserUpdateRequestSchema,
    ) -> User:
        update_data = data.model_dump(
            exclude_unset=True,
        )

        for key, value in update_data.items():
            setattr(user, key, value)

        return await self._repository.update(user)
