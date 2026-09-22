"""Minimal in-process sliding-window rate limiter.

Hardened for Option A (STATUS.md): bounded memory, evicts expired buckets
and oldest keys. Sufficient for the single-user, single-process deployment
CodeAtlas targets now. When the app is scaled out or exposed publicly this
must be replaced by shared-state limiting (docs/Security_Privacy_And_Ethics.md
§16).
"""

import time
from collections import OrderedDict, deque


class SlidingWindowLimiter:
    def __init__(self, max_events: int, window_seconds: float, max_keys: int = 5000) -> None:
        self.max_events = max_events
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._events: OrderedDict[str, deque[float]] = OrderedDict()

    def _evict_expired(self, now: float) -> None:
        cutoff = now - self.window_seconds
        empty_keys = []
        for key, events in self._events.items():
            while events and events[0] < cutoff:
                events.popleft()
            if not events:
                empty_keys.append(key)
        for key in empty_keys:
            self._events.pop(key, None)

    def _enforce_key_cap(self) -> None:
        while len(self._events) > self.max_keys:
            self._events.popitem(last=False)

    def allow(self, key: str) -> bool:
        """Record one event for `key` and report whether it is within limits."""
        now = time.monotonic()
        # Opportunistic cleanup keeps the map bounded.  Running on every
        # allow() is cheap (only empty buckets are removed) and prevents
        # unbounded growth behind a reverse proxy where many IPs appear.
        if len(self._events) > 100:
            self._evict_expired(now)
            self._enforce_key_cap()

        events = self._events.get(key)
        if events is None:
            events = deque()
            self._events[key] = events
        else:
            # Move to end for LRU ordering
            self._events.move_to_end(key)
            cutoff = now - self.window_seconds
            while events and events[0] < cutoff:
                events.popleft()

        if len(events) >= self.max_events:
            return False

        events.append(now)
        self._enforce_key_cap()
        return True

    def purge_expired(self) -> int:
        """Remove all buckets whose window has fully expired. Returns count purged."""
        before = len(self._events)
        self._evict_expired(time.monotonic())
        return before - len(self._events)

    def reset(self) -> None:
        """Clear all tracked state (used by tests to stay isolated)."""
        self._events.clear()


# Login attempts are strictly limited; register/logout are cheap operations.
login_limiter = SlidingWindowLimiter(max_events=5, window_seconds=60.0)

# Code executions are expensive operations (security doc §16).
execution_limiter = SlidingWindowLimiter(max_events=10, window_seconds=60.0)
