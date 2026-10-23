# app/merge/models.py

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel
from uuid_extensions import uuid7

from app.db.types import UTCDateTime


class MergeProof(SQLModel, table=True):
    """Short-lived single-use proof that one user controls another account.

    It is bound to both users: the target (the signed-in user who asks for
    the merge) and the source (the account that is proven and merged away).
    """

    __tablename__ = "merge_proofs"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    target_user_id: str = Field(foreign_key="users.id", index=True)
    source_user_id: str = Field(foreign_key="users.id", index=True)
    expires_at: datetime = Field(sa_type=UTCDateTime, nullable=False)
    # A proof of an account with two-factor authentication stays unconfirmed
    # until the code sent to that account is entered (challenge_id).
    confirmed: bool = Field(default=False, nullable=False)
    challenge_id: str | None = Field(default=None)
    used: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=UTCDateTime,
        nullable=False,
    )
