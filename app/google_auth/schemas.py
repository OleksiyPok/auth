# app/google_auth/schemas.py

from typing import TypeAlias

from pydantic import BaseModel

from app.merge.schemas import MergeProofResponseSchema
from app.sessions.schemas import AuthenticationResponseSchema


class GoogleAuthorizationResponseSchema(BaseModel):
    authorization_url: str


class GoogleLoginResponseSchema(AuthenticationResponseSchema):
    # True when a new user was created and the verified Google email matches an
    # existing email sign-in method. Nothing is linked: the client may offer it.
    email_match: bool = False


class GoogleLinkResponseSchema(BaseModel):
    identity_id: str
    message: str = "Google account linked"


# What the callback returns, depending on the purpose of the OAuth state:
# login, link or merge.
GoogleCallbackResponse: TypeAlias = (
    GoogleLoginResponseSchema | GoogleLinkResponseSchema | MergeProofResponseSchema
)
