# app/merge/services/proof_service.py

from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.identifiers import normalize_email, normalize_username
from app.email_auth.repository.repository_interface import (
    EmailIdentityRepositoryInterface,
)
from app.infrastructure.password import verify_password
from app.merge.exceptions import InvalidMergeCredentialsError
from app.merge.models import MergeProof
from app.merge.repository.repository_interface import MergeProofRepositoryInterface
from app.merge.schemas import (
    MergeProofEmailRequestSchema,
    MergeProofResponseSchema,
    MergeProofUsernameRequestSchema,
)
from app.merge.services.proof_service_interface import MergeProofServiceInterface
from app.username_auth.repository.repository_interface import (
    UsernameIdentityRepositoryInterface,
)
from app.users.exceptions import UserNotFoundError
from app.users.models import User
from app.users.repository.repository_interface import UserRepositoryInterface
from app.users.services.service_interface import UserServiceInterface


class MergeProofService(MergeProofServiceInterface):

    def __init__(
        self,
        merge_proof_repository: MergeProofRepositoryInterface,
        user_repository: UserRepositoryInterface,
        user_service: UserServiceInterface,
        username_identity_repository: UsernameIdentityRepositoryInterface,
        email_identity_repository: EmailIdentityRepositoryInterface,
    ):
        self._merge_proof_repository = merge_proof_repository
        self._user_repository = user_repository
        self._user_service = user_service
        self._username_identity_repository = username_identity_repository
        self._email_identity_repository = email_identity_repository

    async def create_by_username(
        self,
        target_user: User,
        data: MergeProofUsernameRequestSchema,
    ) -> MergeProofResponseSchema:
        identity = await self._username_identity_repository.get_by_username(
            normalize_username(data.username)
        )

        if identity is None or not verify_password(
            data.password, identity.password_hash
        ):
            raise InvalidMergeCredentialsError()

        return await self.create_for_source(target_user, identity.user_id)

    async def create_by_email(
        self,
        target_user: User,
        data: MergeProofEmailRequestSchema,
    ) -> MergeProofResponseSchema:
        identity = await self._email_identity_repository.get_by_email(
            normalize_email(data.email)
        )

        if identity is None or not verify_password(
            data.password, identity.password_hash
        ):
            raise InvalidMergeCredentialsError()

        return await self.create_for_source(target_user, identity.user_id)

    async def create_for_source(
        self,
        target_user: User,
        source_user_id: str,
    ) -> MergeProofResponseSchema:
        source_user = await self._user_repository.get_by_id(source_user_id)

        if source_user is None:
            raise UserNotFoundError()

        # Refuses the same user, an inactive source or target, and the last
        # active superadmin as a source, before any proof exists.
        await self._user_service.validate_merge(source_user, target_user)

        proof = await self._merge_proof_repository.create(
            MergeProof(
                target_user_id=target_user.id,
                source_user_id=source_user.id,
                expires_at=(
                    datetime.now(timezone.utc)
                    + timedelta(minutes=settings.MERGE_PROOF_EXPIRE_MINUTES)
                ),
            )
        )

        return MergeProofResponseSchema(
            proof_id=proof.id,
            expires_at=proof.expires_at.isoformat(),
        )
