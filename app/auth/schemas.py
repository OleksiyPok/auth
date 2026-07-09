# app/auth/schemas.py

from sqlmodel import SQLModel


class RegisterResponseSchema(SQLModel):
    id: str


class RegisterRequestSchema(SQLModel):
    login: str
