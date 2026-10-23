# app/google_auth/models.py

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel
from uuid_extensions import uuid7

from app.db.types import UTCDateTime
from app.google_auth.purpose import GoogleOAuthPurpose


class GoogleIdentity(SQLModel, table=True):
    __tablename__ = "google_identities"

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

    state: str = Field(
        index=True,
        unique=True,
        nullable=False,
    )

    code_verifier: str = Field(
        nullable=False,
    )

    purpose: str = Field(
        default=GoogleOAuthPurpose.LOGIN,
        nullable=False,
        max_length=16,
    )

    # The user who links a Google account; empty for login states.
    user_id: str | None = Field(
        default=None,
        foreign_key="users.id",
        index=True,
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
