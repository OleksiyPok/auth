# app/users/models.py

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel

from app.db.types import UTCDateTime


class UserBase(SQLModel):
    username: str
    email: str


class User(UserBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    password_hash: str | None = Field(default=None)
    refresh_token: str | None = Field(default=None, nullable=True)

    auth_provider: str = Field(default="local")

    created_at: datetime = Field(
        sa_column=Column(UTCDateTime(), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    updated_at: datetime = Field(
        sa_column=Column(UTCDateTime(), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
