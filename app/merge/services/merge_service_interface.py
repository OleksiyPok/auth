# app/merge/services/merge_service_interface.py

from abc import ABC, abstractmethod


class MergeServiceInterface(ABC):

    @abstractmethod
    async def merge(
        self,
        target_user_id: str,
        source_user_id: str,
    ) -> None: ...
