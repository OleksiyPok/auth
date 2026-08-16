# app/infrastructure/email/dev_router.py

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr

from app.infrastructure.email.base import EmailService
from app.infrastructure.email.manager import EmailManager


router = APIRouter(
    prefix="/dev/email",
    tags=["Development"],
)


class TestEmailRequest(BaseModel):
    to: EmailStr
    subject: str = "Test email"
    body: str = "This is a test email."


async def get_email_service() -> EmailService:
    return EmailManager()


@router.post(
    "/send",
    summary="Send test email",
    description="Development endpoint for testing the configured email service.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def send_test_email(
    data: TestEmailRequest,
    service: Annotated[
        EmailService,
        Depends(get_email_service),
    ],
) -> None:
    await service.send(
        to=str(data.to),
        subject=data.subject,
        body=data.body,
    )