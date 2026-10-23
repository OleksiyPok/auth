# app/merge/services/merge_service_interface.py

from abc import ABC, abstractmethod

from app.users.models import User


class MergeServiceInterface(ABC):

    @abstractmethod
    async def merge(
        self,
        target_user_id: str,
        source_user_id: str,
    ) -> None: ...

    @abstractmethod
    async def merge_by_proof(
        self,
        current_user: User,
        proof_id: str,
    ) -> None: ...
