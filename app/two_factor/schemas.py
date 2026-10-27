# app/two_factor/schemas.py

from pydantic import BaseModel

from app.sessions.schemas import AuthenticationResponseSchema


class TwoFactorChallengeResponseSchema(BaseModel):
    challenge_id: str
    expires_at: str
    message: str = "Verification code sent to your email"


class TwoFactorAddEmailMethodRequestSchema(BaseModel):
    email: str


class TwoFactorResendRequestSchema(BaseModel):
    challenge_id: str


class TwoFactorRecoveryCodesResponseSchema(BaseModel):
    # Shown once: only hashes are stored.
    codes: list[str]


class TwoFactorConfirmRequestSchema(BaseModel):
    challenge_id: str
    code: str


class TwoFactorLoginConfirmResponseSchema(AuthenticationResponseSchema):
    pass


class TwoFactorMethodSchema(BaseModel):
    id: str
    type: str
    destination: str
    is_default: bool


class TwoFactorStatusResponseSchema(BaseModel):
    enabled: bool
    methods: list[TwoFactorMethodSchema]
