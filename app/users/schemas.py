# app/users/schemas.py

from datetime import datetime

from pydantic import BaseModel


class UserUpdateRequestSchema(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserRoleAssignRequestSchema(BaseModel):
    role: str


class UserResponseSchema(BaseModel):
    id: str
    login: str
    email: str
    first_name: str
    last_name: str
    role: str


class UserDetailedResponseSchema(UserResponseSchema):
    is_active: bool
    created_at: datetime
    updated_at: datetime
