# app/auth/schemas.py

from pydantic import BaseModel, ConfigDict


class RegisterRequestSchema(BaseModel):
    login: str
    password: str
    email: str
    first_name: str
    last_name: str


class RegisterResponseSchema(BaseModel):
    id: str
    login: str
    email: str
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class LoginRequestSchema(BaseModel):
    login: str
    password: str


class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
