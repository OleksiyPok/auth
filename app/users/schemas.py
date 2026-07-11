# app/users/schemas.py

from sqlmodel import SQLModel


class UserResponseSchema(SQLModel):
    id: str
    login: str


class DeleteUserResponseSchema(SQLModel):
    id: str
