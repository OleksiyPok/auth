from pydantic import BaseModel

from app.sessions.schemas import AuthenticationResponseSchema


class EmailRegisterRequestSchema(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class EmailRegisterResponseSchema(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str


class EmailLoginRequestSchema(BaseModel):
    email: str
    password: str


# AuthenticationResponseSchema is returned by login and can either contain
# tokens or a two-factor challenge.
AuthenticationResponse = AuthenticationResponseSchema
