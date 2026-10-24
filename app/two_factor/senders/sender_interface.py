# app/two_factor/senders/sender_interface.py

from abc import ABC, abstractmethod

from app.two_factor.models import TwoFactorMethod


class TwoFactorSenderInterface(ABC):
    """Delivers a verification code to a 2FA method."""

    @abstractmethod
    async def send_code(
        self,
        method: TwoFactorMethod,
        subject: str,
        code: str,
        expires_in_minutes: int,
    ) -> None: ...
