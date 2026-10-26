# app/contacts/models.py

from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel
from uuid_extensions import uuid7

from app.db.types import UTCDateTime


class Contact(SQLModel, table=True):
    """Contact data of a user: an unverified email or phone.

    It is never used to sign in or to link accounts.
    """

    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("user_id", "type", "value"),)

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    type: str = Field(max_length=16)
    value: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )
