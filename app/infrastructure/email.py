import asyncio
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def _send_email_sync(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(
        settings.EMAIL_SMTP_HOST,
        settings.EMAIL_SMTP_PORT,
        timeout=settings.EMAIL_SMTP_TIMEOUT,
    ) as smtp:
        if settings.EMAIL_SMTP_STARTTLS:
            smtp.starttls()

        if settings.EMAIL_SMTP_USERNAME:
            smtp.login(
                settings.EMAIL_SMTP_USERNAME,
                settings.EMAIL_SMTP_PASSWORD,
            )

        smtp.send_message(message)


async def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    await asyncio.to_thread(
        _send_email_sync,
        recipient,
        subject,
        body,
    )
