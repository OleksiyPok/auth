# app/sessions/models.py

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel
from uuid_extensions import uuid7

from app.db.types import UTCDateTime


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: str = Field(
        default_factory=lambda: str(uuid7()),
        primary_key=True,
    )

    user_id: str = Field(
        index=True,
        foreign_key="users.id",
    )

    provider: str = Field(
        default="username",
        max_length=32,
    )

    refresh_token_hash: str

    is_active: bool = Field(
        default=True,
        nullable=False,
    )

    ip_address: str | None = Field(
        default=None,
        max_length=45,
    )

    user_agent: str | None = Field(
        default=None,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )

    last_used_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )

    revoked_at: datetime | None = Field(
        default=None,
        sa_type=UTCDateTime,
    )

    expires_at: datetime = Field(
        sa_type=UTCDateTime,
        nullable=False,
    )
