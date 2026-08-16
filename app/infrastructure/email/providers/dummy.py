# app/infrastructure/email/providers/dummy.py

from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.infrastructure.email.base import EmailService

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DUMMY_LOG_DIR = PROJECT_ROOT / "logs" / "email_dummy_logs"
DUMMY_LOG_PREFIX = "emails"
DUMMY_LOG_DATE_FORMAT = "%Y-%m-%d"

# Commonly accepted international date formats:
# "%Y-%m-%d"     -> 2026-03-04      (ISO 8601 — international standard)
# "%Y%m%d"       -> 20260304        (ISO 8601 basic format)
# "%Y-%m"        -> 2026-03         (ISO 8601 year-month)
# "%Y"           -> 2026            (ISO 8601 year)
# "%Y-%W"        -> 2026-09         (ISO week date: year-week number)

# Commonly used in DevOps / Linux environments with underscores:
# "%Y_%m_%d"     -> 2026_03_04      (file-friendly format)
# "%Y_%m"        -> 2026_03         (file-friendly year-month)
# "%Y_%m_%d_%H"  -> 2026_03_04_15   (with hour for log rotation)
# "%Y_%m_%d_%H_%M" -> 2026_03_04_15_30   (with minute for high-frequency logs)


def _build_log_path() -> Path:
    current_date = datetime.now().strftime(DUMMY_LOG_DATE_FORMAT)
    return DUMMY_LOG_DIR / f"{DUMMY_LOG_PREFIX}_{current_date}.log"


class DummyEmailService(EmailService):
    def __init__(self):
        self.enabled = getattr(settings, "DUMMY_EMAIL_ENABLED", True)
        DUMMY_LOG_DIR.mkdir(parents=True, exist_ok=True)

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        html: str | None = None,
    ) -> None:
        if not self.enabled:
            return

        log_path = _build_log_path()
        content = html if html else body
        current_datetime = datetime.now().strftime(f"{DUMMY_LOG_DATE_FORMAT} %H:%M")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(
                f"{'═' * 50}\n"
                f"Sent at: {current_datetime}\n"
                f"{'—' * 50}\n"
                f"To: {to}\n"
                f"Subject: {subject}\n"
                f"{'-' * 25}\n"
                f"Body:\n{content}\n"
                "\n"
            )
