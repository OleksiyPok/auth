# app/google_auth/schemas.py

from pydantic import BaseModel


class GoogleAuthorizationResponseSchema(BaseModel):
    authorization_url: str


class GoogleLinkResponseSchema(BaseModel):
    identity_id: str
    message: str = "Google account linked"
