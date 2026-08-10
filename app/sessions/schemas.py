# app/sessions/schemas.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionResponseSchema(BaseModel):
    id: str
    provider: str
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
