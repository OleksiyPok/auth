# app/merge/repository/repository_interface.py

from abc import ABC, abstractmethod

from app.merge.models import MergeProof


class MergeProofRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, proof: MergeProof) -> MergeProof: ...

    @abstractmethod
    async def get_by_id(self, proof_id: str) -> MergeProof | None: ...

    @abstractmethod
    async def mark_confirmed(self, proof: MergeProof) -> MergeProof: ...

    @abstractmethod
    async def mark_used(self, proof: MergeProof) -> MergeProof: ...

    @abstractmethod
    async def delete_by_user_id(self, user_id: str) -> None: ...
