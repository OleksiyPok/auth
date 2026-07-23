# app/users/models.py

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from uuid_extensions import (
    uuid7,
)  # replace with stdlib uuid.uuid7 after upgrading to Python 3.14+

from app.db.types import UTCDateTime
from app.users.enums import UserRole


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    login: str
    password_hash: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(default=UserRole.USER, nullable=False)

    is_active: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(
        sa_column=Column(
            UTCDateTime(),
            nullable=False,
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    updated_at: datetime = Field(
        sa_column=Column(
            UTCDateTime(),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )
