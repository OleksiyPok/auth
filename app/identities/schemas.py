# app/identities/schemas.py

from datetime import datetime

from pydantic import BaseModel

from app.identities.types import IdentityType


class IdentityResponseSchema(BaseModel):
    id: str
    type: IdentityType
    # Username, masked email, or None for Google.
    display_identifier: str | None
    created_at: datetime
