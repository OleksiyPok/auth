# app/google/schemas.py

from pydantic import BaseModel


class GoogleConnectionStatusSchema(BaseModel):
    connected: bool
    google_user_id: str | None = None


class GoogleContactCreateSchema(BaseModel):
    given_name: str
    family_name: str | None = None
    email: str | None = None
    phone: str | None = None


class GoogleContactResponseSchema(BaseModel):
    resource_name: str
    display_name: str | None = None
    email: str | None = None
    phone: str | None = None


class GoogleContactUpdateSchema(BaseModel):
    given_name: str | None = None
    family_name: str | None = None
    email: str | None = None
    phone: str | None = None
