# app/local_auth/models.py

from datetime import datetime, timezone

from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from uuid_extensions import uuid7

from app.db.types import UTCDateTime


class LocalIdentity(SQLModel, table=True):
    __tablename__ = "local_identities"

    id: str = Field(
        default_factory=lambda: str(uuid7()),
        primary_key=True,
    )

    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        unique=True,
    )

    login: str = Field(
        unique=True,
        index=True,
    )

    password_hash: str

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
