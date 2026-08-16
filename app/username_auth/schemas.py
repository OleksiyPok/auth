# app/username_auth/schemas.py

from pydantic import BaseModel


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
    role: str


class LoginRequestSchema(BaseModel):
    login: str
    password: str
