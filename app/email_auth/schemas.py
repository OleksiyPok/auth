# app/email_auth/schemas.py

from pydantic import BaseModel

from app.sessions.schemas import AuthenticationResponseSchema


class EmailRegisterRequestSchema(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class EmailRegisterChallengeResponseSchema(BaseModel):
    registration_id: str
    expires_at: str
    message: str = "Verification code sent to your email"


class EmailRegisterConfirmRequestSchema(BaseModel):
    registration_id: str
    code: str


class EmailRegisterResendRequestSchema(BaseModel):
    registration_id: str


class EmailRegisterResponseSchema(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str


class EmailLoginRequestSchema(BaseModel):
    email: str
    password: str


class EmailLinkRequestSchema(BaseModel):
    email: str
    password: str


class EmailLinkChallengeResponseSchema(BaseModel):
    challenge_id: str
    expires_at: str
    message: str = "Verification code sent to your email"


class EmailLinkConfirmRequestSchema(BaseModel):
    challenge_id: str
    code: str


# AuthenticationResponseSchema is returned by login and can either contain
# tokens or a two-factor challenge.
AuthenticationResponse = AuthenticationResponseSchema
