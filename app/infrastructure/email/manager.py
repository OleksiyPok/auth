# app/infrastructure/email/manager.py

from app.core.config import settings
from app.infrastructure.email.base import EmailService
from app.infrastructure.email.exceptions import ProviderRegisterError
from app.infrastructure.email.registry import EMAIL_PROVIDERS


class EmailManager(EmailService):

    def __init__(self):
        name = settings.EMAIL_SERVICE.strip().lower()

        provider = EMAIL_PROVIDERS.get(name)

        if provider is None:
            raise ProviderRegisterError(f"Email provider '{name}' not registered")

        self._service = provider()

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        html: str | None = None,
    ) -> None:
        await self._service.send(
            to=to,
            subject=subject,
            body=body,
            html=html,
        )
