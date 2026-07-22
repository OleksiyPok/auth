# app/users/schemas.py

from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import SQLModel


class UserUpdateRequestSchema(SQLModel):
    first_name: str | None = None
    last_name: str | None = None


class UserUpdateByAdminRequestSchema(UserUpdateRequestSchema):
    is_active: bool | None = None


class UserResponseSchema(SQLModel):
    id: str
    login: str
    first_name: str
    last_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserDetailedResponseSchema(UserResponseSchema):
    is_active: bool
    created_at: datetime
    updated_at: datetime
