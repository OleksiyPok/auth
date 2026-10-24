# app/two_factor/models.py

from datetime import datetime, timezone

from sqlalchemy import Column, UniqueConstraint
from sqlmodel import Field, SQLModel
from uuid_extensions import uuid7

from app.db.types import UTCDateTime


class UserSecuritySettings(SQLModel, table=True):
    __tablename__ = "user_security_settings"
    __table_args__ = (UniqueConstraint("user_id"),)

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    two_factor_enabled: bool = Field(default=False, nullable=False)

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


class TwoFactorMethod(SQLModel, table=True):
    __tablename__ = "two_factor_methods"
    __table_args__ = (UniqueConstraint("user_id", "type", "value"),)

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    type: str = Field(max_length=16)
    value: str
    verified: bool = Field(default=False, nullable=False)
    is_default: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )


class TwoFactorChallenge(SQLModel, table=True):
    __tablename__ = "two_factor_challenges"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    identity_id: str | None = Field(default=None, index=True)
    identity_type: str | None = Field(default=None, max_length=16)
    purpose: str = Field(max_length=32, index=True)
    code_hash: str
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = None
    expires_at: datetime = Field(sa_type=UTCDateTime, nullable=False)
    attempts: int = Field(default=0, nullable=False)
    used: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )
