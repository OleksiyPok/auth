# app/users/schemas.py

from datetime import datetime

from pydantic import BaseModel

from app.users.status import UserStatus


class UserUpdateRequestSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserRoleAssignRequestSchema(BaseModel):
    role: str


class UserResponseSchema(BaseModel):
    id: str
    first_name: str
    last_name: str
    role: str


class UserDetailedResponseSchema(UserResponseSchema):
    status: UserStatus
    created_at: datetime
    updated_at: datetime
