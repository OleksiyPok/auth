# app/merge/schemas.py

from pydantic import BaseModel


class MergeProofUsernameRequestSchema(BaseModel):
    username: str
    password: str


class MergeProofEmailRequestSchema(BaseModel):
    email: str
    password: str


class MergeProofResponseSchema(BaseModel):
    proof_id: str
    expires_at: str
    # True when a code was sent to the account that is proven: the proof is
    # usable only after POST /users/me/merge/proofs/confirm.
    requires_two_factor: bool = False
    challenge_id: str | None = None


class MergeProofConfirmRequestSchema(BaseModel):
    proof_id: str
    code: str
