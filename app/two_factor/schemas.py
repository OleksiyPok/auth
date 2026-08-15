from pydantic import BaseModel

from app.sessions.schemas import AuthenticationResponseSchema


class TwoFactorChallengeResponseSchema(BaseModel):
    challenge_id: str
    expires_at: str
    message: str = "Verification code sent to your email"


class TwoFactorConfirmRequestSchema(BaseModel):
    challenge_id: str
    code: str


class TwoFactorLoginConfirmResponseSchema(AuthenticationResponseSchema):
    pass
