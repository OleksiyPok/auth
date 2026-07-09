# app/users/models.py

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from uuid_extensions import (
    uuid7,
)
# TODO: replace with stdlib uuid.uuid7 after upgrading to Python 3.14+

from app.db.types import UTCDateTime


class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    login: str

    created_at: datetime = Field(
        sa_column=Column(UTCDateTime(), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    updated_at: datetime = Field(
        sa_column=Column(UTCDateTime(), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
