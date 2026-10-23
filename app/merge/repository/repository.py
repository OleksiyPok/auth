# app/merge/repository/repository.py

from sqlalchemy import delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.merge.models import MergeProof
from app.merge.repository.repository_interface import MergeProofRepositoryInterface


class MergeProofRepository(MergeProofRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, proof: MergeProof) -> MergeProof:
        self._session.add(proof)
        await self._session.flush()
        await self._session.refresh(proof)
        return proof

    async def get_by_id(self, proof_id: str) -> MergeProof | None:
        result = await self._session.execute(
            select(MergeProof).where(MergeProof.id == proof_id)
        )
        return result.scalar_one_or_none()

    async def mark_used(self, proof: MergeProof) -> MergeProof:
        proof.used = True
        self._session.add(proof)
        await self._session.flush()
        await self._session.refresh(proof)
        return proof

    async def delete_by_user_id(self, user_id: str) -> None:
        await self._session.execute(
            delete(MergeProof).where(
                or_(
                    col(MergeProof.target_user_id) == user_id,
                    col(MergeProof.source_user_id) == user_id,
                )
            )
        )
