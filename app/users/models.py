# app/users/models.py

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from app.db.types import UTCDateTime


class UserBase(SQLModel):
    login: str


class User(UserBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    created_at: datetime = Field(
        sa_column=Column(UTCDateTime(), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    updated_at: datetime = Field(
        sa_column=Column(UTCDateTime(), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
