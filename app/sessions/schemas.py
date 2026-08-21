# app/sessions/schemas.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionResponseSchema(BaseModel):
    id: str
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthenticationResponseSchema(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    requires_two_factor: bool = False
    challenge_id: str | None = None
