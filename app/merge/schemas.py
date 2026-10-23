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
