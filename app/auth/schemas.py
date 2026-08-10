# app/auth/schemas.py

from pydantic import BaseModel


class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
