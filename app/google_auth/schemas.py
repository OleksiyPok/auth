# app/google_auth/schemas.py

from pydantic import BaseModel

from app.merge.schemas import MergeProofResponseSchema
from app.sessions.schemas import AuthenticationResponseSchema


class GoogleAuthorizationResponseSchema(BaseModel):
    authorization_url: str


class GoogleLinkResponseSchema(BaseModel):
    identity_id: str
    message: str = "Google account linked"


# What the callback returns, depending on the purpose of the OAuth state:
# login, link or merge.
GoogleCallbackResponse = (
    AuthenticationResponseSchema | GoogleLinkResponseSchema | MergeProofResponseSchema
)
