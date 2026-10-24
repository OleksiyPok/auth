# app/two_factor/senders/email_sender.py

from app.infrastructure.email.base import EmailService
from app.two_factor.models import TwoFactorMethod
from app.two_factor.senders.sender_interface import TwoFactorSenderInterface


class EmailTwoFactorSender(TwoFactorSenderInterface):
    """Sends the code to the address stored in the method."""

    def __init__(self, email_service: EmailService):
        self._email_service = email_service

    async def send_code(
        self,
        method: TwoFactorMethod,
        subject: str,
        code: str,
        expires_in_minutes: int,
    ) -> None:
        await self._email_service.send(
            to=method.value,
            subject=subject,
            body=(
                f"Your verification code is: {code}\n\n"
                f"The code expires in {expires_in_minutes} minutes."
            ),
        )
