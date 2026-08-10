# app/users/models.py

from datetime import datetime, timezone

from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from uuid_extensions import (
    uuid7,
)  # replace with stdlib uuid.uuid7 after upgrading to Python 3.14+

from app.auth.rbac.role_permissions import validate_role
from app.auth.rbac.roles import DEFAULT_ROLE
from app.db.types import UTCDateTime


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)

    email: str
    first_name: str
    last_name: str
    role: str = Field(default=DEFAULT_ROLE, nullable=False)

    is_active: bool = Field(default=True, nullable=False)

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

    def __init__(self, **data):
        if "role" in data:
            data["role"] = validate_role(data["role"])
        super().__init__(**data)
