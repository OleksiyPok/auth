# app/infrastructure/email/providers/mailjet.py

from asyncio import to_thread

from mailjet_rest import Client

from app.core.config import settings
from app.infrastructure.email.base import EmailService
from app.infrastructure.email.exceptions import (
    ExternalServiceError,
    ProviderConfigurationError,
)


class MailjetEmailService(EmailService):
    def __init__(self):
        if not settings.MAILJET_API_KEY or not settings.MAILJET_SECRET_KEY:
            raise ProviderConfigurationError("Mailjet credentials are not configured")

        self.client = Client(
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            version="v3.1",
        )

    async def send(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> None:
        message = {
            "Messages": [
                {
                    "From": {
                        "Email": settings.MAIL_FROM_EMAIL,
                        "Name": settings.MAIL_FROM_NAME,
                    },
                    "To": [{"Email": to}],
                    "Subject": subject,
                    "TextPart": body if not html else None,
                    "HTMLPart": html,
                }
            ]
        }

        response = await to_thread(self.client.send.create, data=message)

        if response.status_code >= 400:
            raise ExternalServiceError(f"Mailjet email failed: {response.text}")
