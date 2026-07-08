# app/auth/schemas.py

from app.users.models import UserBase


class RegisterResponseSchema(UserBase):
    id: str


class RegisterRequestSchema(UserBase):
    login: str
