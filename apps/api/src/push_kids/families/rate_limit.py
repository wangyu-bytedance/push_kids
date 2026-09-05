from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from push_kids.platform.errors import TooManyRequestsError


class InvitePreviewRateLimiter:
    """Small in-process guard for the authenticated invite preview endpoint."""

    def __init__(self, limit: int = 20, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, subject_hmac: str) -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            attempts = self._attempts[subject_hmac]
            while attempts and attempts[0] <= cutoff:
                attempts.popleft()
            if len(attempts) >= self.limit:
                raise TooManyRequestsError("邀请查询过于频繁，请稍后再试")
            attempts.append(now)
