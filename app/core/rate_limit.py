# app/core/rate_limit.py

"""Simple in-memory rate limiting (sliding window).

The counters live in the memory of one process: they are reset on restart and
are not shared between workers or servers. For several workers move them to
Redis.

The client address is `request.client.host`. Behind a reverse proxy it is the
proxy address, so proxy headers must be configured first (for example,
`uvicorn --proxy-headers --forwarded-allow-ips=...`).
"""

import math
import time
from collections import deque
from collections.abc import Awaitable, Callable
from typing import NamedTuple

from fastapi import Request

from app.core.exceptions import RateLimitExceededError

MINUTE = 60
HOUR = 60 * MINUTE


class Rule(NamedTuple):
    name: str
    limit: int
    window_seconds: int


# Per client IP.
REGISTER_IP = Rule("register_ip", 10, HOUR)
LOGIN_IP = Rule("login_ip", 20, 10 * MINUTE)
CONFIRM_IP = Rule("confirm_ip", 20, 10 * MINUTE)
SEND_CODE_IP = Rule("send_code_ip", 10, 10 * MINUTE)

# Per identifier (normalized email or username), whatever the IP is.
REGISTER_EMAIL = Rule("register_email", 3, HOUR)
REGISTER_USERNAME = Rule("register_username", 3, HOUR)
LOGIN_EMAIL = Rule("login_email", 10, 15 * MINUTE)
LOGIN_USERNAME = Rule("login_username", 10, 15 * MINUTE)


class RateLimiter:

    _CLEANUP_INTERVAL_SECONDS = MINUTE

    def __init__(self) -> None:
        # key -> (window_seconds, timestamps of the hits inside the window)
        self._hits: dict[str, tuple[int, deque[float]]] = {}
        self._last_cleanup = time.monotonic()

    def hit(self, rule: Rule, key: str) -> None:
        """Count one request; raise RateLimitExceededError over the limit."""
        now = time.monotonic()

        if now - self._last_cleanup >= self._CLEANUP_INTERVAL_SECONDS:
            self._cleanup(now)

        _, timestamps = self._hits.setdefault(
            f"{rule.name}:{key}",
            (rule.window_seconds, deque()),
        )

        while timestamps and now - timestamps[0] >= rule.window_seconds:
            timestamps.popleft()

        if len(timestamps) >= rule.limit:
            retry_after = math.ceil(rule.window_seconds - (now - timestamps[0]))
            raise RateLimitExceededError(
                f"Too many requests, try again in {retry_after} seconds"
            )

        timestamps.append(now)

    def reset(self) -> None:
        self._hits.clear()

    def _cleanup(self, now: float) -> None:
        # Without it the keys of one-off clients would stay in memory forever.
        for key, (window_seconds, timestamps) in list(self._hits.items()):
            if not timestamps or now - timestamps[-1] >= window_seconds:
                del self._hits[key]

        self._last_cleanup = now


rate_limiter = RateLimiter()


def limit_by_ip(rule: Rule) -> Callable[[Request], Awaitable[None]]:
    """Dependency: limits the requests of one client IP by the rule."""

    async def dependency(request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        rate_limiter.hit(rule, ip)

    return dependency
