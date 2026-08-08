# app/google/models.py

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel
from uuid_extensions import uuid7

from app.db.types import UTCDateTime


class GoogleAccount(SQLModel, table=True):
    __tablename__ = "google_accounts"

    id: str = Field(
        default_factory=lambda: str(uuid7()),
        primary_key=True,
    )

    user_id: str = Field(
        index=True,
        unique=True,
        foreign_key="users.id",
    )

    google_user_id: str = Field(
        index=True,
        unique=True,
    )

    access_token: str = Field(
        nullable=False,
    )

    refresh_token: str = Field(
        nullable=False,
    )

    token_expires_at: datetime = Field(
        nullable=False,
        sa_type=UTCDateTime,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=UTCDateTime,
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=UTCDateTime,
    )


class GoogleOAuthState(SQLModel, table=True):
    __tablename__ = "google_oauth_states"

    id: str = Field(
        default_factory=lambda: str(uuid7()),
        primary_key=True,
    )

    user_id: str = Field(
        index=True,
        foreign_key="users.id",
    )

    state: str = Field(
        index=True,
        unique=True,
        nullable=False,
    )

    code_verifier: str = Field(
        nullable=False,
    )

    expires_at: datetime = Field(
        nullable=False,
        sa_type=UTCDateTime,
    )

    used: bool = Field(
        default=False,
        nullable=False,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=UTCDateTime,
    )
