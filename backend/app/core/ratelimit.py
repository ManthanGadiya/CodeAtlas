"""Minimal in-process sliding-window rate limiter.

Sufficient for the single-user, single-process deployment CodeAtlas
targets now. When the app is scaled out or exposed publicly this must be
replaced by shared-state limiting (docs/Security_Privacy_And_Ethics.md
§16); tracked in STATUS.md known limitations.
"""

import time
from collections import deque


class SlidingWindowLimiter:
    def __init__(self, max_events: int, window_seconds: float) -> None:
        self.max_events = max_events
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = {}

    def allow(self, key: str) -> bool:
        """Record one event for `key` and report whether it is within limits."""
        now = time.monotonic()
        events = self._events.setdefault(key, deque())

        cutoff = now - self.window_seconds
        while events and events[0] < cutoff:
            events.popleft()

        if len(events) >= self.max_events:
            return False

        events.append(now)
        return True

    def reset(self) -> None:
        """Clear all tracked state (used by tests to stay isolated)."""
        self._events.clear()


# Login attempts are strictly limited; register/logout are cheap operations.
login_limiter = SlidingWindowLimiter(max_events=5, window_seconds=60.0)

# Code executions are expensive operations (security doc §16).
execution_limiter = SlidingWindowLimiter(max_events=10, window_seconds=60.0)
