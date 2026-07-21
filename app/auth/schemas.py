# app/auth/schemas.py

from pydantic import ConfigDict
from sqlmodel import SQLModel


class RegisterRequestSchema(SQLModel):
    login: str
    first_name: str
    last_name: str


class RegisterResponseSchema(SQLModel):
    id: str
    login: str
    first_name: str
    last_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)
