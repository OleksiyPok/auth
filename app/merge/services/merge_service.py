# app/merge/services/merge_service.py

from app.identities.services.service_interface import IdentityServiceInterface
from app.merge.exceptions import MergeTypeConflictError
from app.merge.services.merge_service_interface import MergeServiceInterface
from app.two_factor.repository.repository_interface import TwoFactorRepositoryInterface
from app.users.exceptions import UserNotFoundError
from app.users.repository.repository_interface import UserRepositoryInterface
from app.users.services.service_interface import UserServiceInterface
from app.users.status import UserStatus


class MergeService(MergeServiceInterface):
    """Move the sign-in methods of the source user to the target user.

    Everything runs in the transaction of the request: if any step fails,
    nothing is changed.
    """

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        user_service: UserServiceInterface,
        identity_service: IdentityServiceInterface,
        two_factor_repository: TwoFactorRepositoryInterface,
    ):
        self._user_repository = user_repository
        self._user_service = user_service
        self._identity_service = identity_service
        self._two_factor_repository = two_factor_repository

    async def merge(
        self,
        target_user_id: str,
        source_user_id: str,
    ) -> None:
        # Both users are locked in a fixed order, so two merges of the same
        # pair cannot deadlock or run at the same time (PostgreSQL).
        target, source = await self._user_repository.get_pair_for_update(
            target_user_id,
            source_user_id,
        )

        if target is None or source is None:
            raise UserNotFoundError()

        await self._user_service.validate_merge(source, target)

        conflicts = await self._identity_service.get_type_conflicts(
            source.id,
            target.id,
        )

        if conflicts:
            raise MergeTypeConflictError(
                "Both accounts have a sign-in method of the same type: "
                + ", ".join(conflicts)
            )

        for identity in await self._identity_service.list_identities(source.id):
            await self._identity_service.transfer_identity(identity, target.id)

        # The two-factor settings of the source do not carry over: the target
        # keeps its own.
        await self._two_factor_repository.delete_by_user_id(source.id)

        # Revokes all sessions of the source and keeps the account itself.
        await self._user_service.deactivate_user(
            current_user=target,
            target_user=source,
            status=UserStatus.DEACTIVATED_BY_MERGE,
        )
