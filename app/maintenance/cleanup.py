# app/maintenance/cleanup.py

import asyncio
import logging

from app.db.session import session_factory
from app.email_auth.repository.repository import EmailIdentityRepository
from app.google_auth.repository.repository import GoogleAuthRepository
from app.two_factor.repository.repository import TwoFactorRepository

logger = logging.getLogger(__name__)


async def run_cleanup_once() -> None:
    """Delete expired or used short-lived rows in one transaction."""
    async with session_factory() as session:
        async with session.begin():
            await EmailIdentityRepository(session).delete_expired_registrations()
            await GoogleAuthRepository(session).delete_expired_or_used_oauth_states()
            await TwoFactorRepository(session).delete_expired_or_used_challenges()


async def run_cleanup_loop(interval_seconds: int) -> None:
    """Run the cleanup forever; an error in one run does not stop the loop."""
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            await run_cleanup_once()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Periodic cleanup failed")
