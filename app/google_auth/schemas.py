# app/google_auth/schemas.py

from pydantic import BaseModel


class GoogleConnectionStatusSchema(BaseModel):
    connected: bool
    google_user_id: str | None = None


class GoogleAuthorizationResponseSchema(BaseModel):
    authorization_url: str
