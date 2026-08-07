# app/users/service.py

from app.auth.rbac.role_permissions import validate_role
from app.auth.rbac.roles import Role
from app.users.exceptions import (  # CannotDeactivateSelfError,
    CannotChangeOwnRoleError,
    LastSuperadminDeactivationError,
    UserNotFoundError,
)
from app.users.models import User
from app.users.repository_interface import UserRepositoryInterface
from app.users.schemas import UserRoleAssignRequestSchema, UserUpdateRequestSchema
from app.users.service_interface import UserServiceInterface


class UserService(UserServiceInterface):

    def __init__(
        self,
        repository: UserRepositoryInterface,
    ):
        self._repository = repository

    async def get_by_id(self, user_id: str) -> User:
        user = await self._repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()
        return user

    async def get_by_login(self, login: str) -> User:
        user = await self._repository.get_by_login(login)

        if user is None:
            raise UserNotFoundError()

        return user

    async def get_all(self) -> list[User]:
        return await self._repository.get_all()

    async def update_self(self, user: User, data: UserUpdateRequestSchema) -> User:

        return await self._update(user, data)

    async def delete(self, user_id: str) -> User:
        user = await self.get_by_id(user_id)

        return await self._repository.delete(user)

    async def change_role(
        self, user_id: str, role_data: UserRoleAssignRequestSchema, current_user_id: str
    ) -> User:
        user = await self.get_by_id(user_id)

        # Validate the requested role using existing RBAC validation
        validated_role = validate_role(role_data.role)

        # Prevent users from changing their own role
        if current_user_id == user.id:
            raise CannotChangeOwnRoleError()

        user.role = validated_role
        return await self._repository.update(user)

    async def deactivate_user(
        self,
        current_user: User,
        target_user: User,
    ) -> User:
        # if current_user.id == target_user.id:
        #     raise CannotDeactivateSelfError()

        if target_user.role == Role.SUPERADMIN:
            count = await self._repository.count_active_superadmins()
            if count == 1:
                raise LastSuperadminDeactivationError()

        return await self._repository.deactivate(target_user)

    async def _update(
        self,
        user: User,
        data: UserUpdateRequestSchema,
    ) -> User:

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user, key, value)

        return await self._repository.update(user)
