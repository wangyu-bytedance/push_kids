from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from push_kids.platform.errors import TooManyRequestsError


class InvitePreviewRateLimiter:
    """In-process guard for authenticated invite credential lookups."""

    def __init__(
        self,
        token_limit: int = 20,
        token_window_seconds: int = 60,
        code_limit: int = 5,
        code_window_seconds: int = 15 * 60,
    ) -> None:
        self.token_limit = token_limit
        self.token_window_seconds = token_window_seconds
        self.code_limit = code_limit
        self.code_window_seconds = code_window_seconds
        self._attempts: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, subject_hmac: str, credential: str) -> None:
        is_manual_code = len(credential) == 6 and credential.isascii() and credential.isdigit()
        kind = "manual_code" if is_manual_code else "share_token"
        limit = self.code_limit if is_manual_code else self.token_limit
        window_seconds = self.code_window_seconds if is_manual_code else self.token_window_seconds
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            attempts = self._attempts[(subject_hmac, kind)]
            while attempts and attempts[0] <= cutoff:
                attempts.popleft()
            if len(attempts) >= limit:
                raise TooManyRequestsError("邀请查询过于频繁，请稍后再试")
            attempts.append(now)
