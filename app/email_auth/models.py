# app/email_auth/models.py

from datetime import datetime, timezone

from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from uuid_extensions import uuid7

from app.db.types import UTCDateTime


class EmailIdentity(SQLModel, table=True):
    __tablename__ = "email_identities"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, unique=True)
    email: str = Field(unique=True, index=True)
    password_hash: str

    created_at: datetime = Field(
        sa_column=Column(UTCDateTime(), nullable=False),
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


class EmailRegistration(SQLModel, table=True):
    __tablename__ = "email_registrations"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    email: str = Field(index=True)
    first_name: str
    last_name: str
    password_hash: str
    code_hash: str
    expires_at: datetime = Field(sa_type=UTCDateTime, nullable=False)
    attempts: int = Field(default=0, nullable=False)
    last_sent_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )


class EmailLinkRequest(SQLModel, table=True):
    """A pending request to add an email identity to an existing user."""

    __tablename__ = "email_link_requests"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    email: str = Field(index=True)
    password_hash: str
    code_hash: str
    expires_at: datetime = Field(sa_type=UTCDateTime, nullable=False)
    attempts: int = Field(default=0, nullable=False)
    last_sent_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )
