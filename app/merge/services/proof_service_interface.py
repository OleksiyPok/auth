# app/merge/services/proof_service_interface.py

from abc import ABC, abstractmethod

from app.merge.schemas import (
    MergeProofEmailRequestSchema,
    MergeProofResponseSchema,
    MergeProofUsernameRequestSchema,
)
from app.users.models import User


class MergeProofServiceInterface(ABC):

    @abstractmethod
    async def create_by_username(
        self,
        target_user: User,
        data: MergeProofUsernameRequestSchema,
    ) -> MergeProofResponseSchema: ...

    @abstractmethod
    async def create_by_email(
        self,
        target_user: User,
        data: MergeProofEmailRequestSchema,
    ) -> MergeProofResponseSchema: ...
