"""Bound preview signing work in a single-process staging runtime."""

from threading import Lock
from time import monotonic

from push_kids.platform.errors import TooManyRequestsError


class MediaPreviewLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._windows: dict[str, tuple[float, int]] = {}

    def check(self, actor: str) -> None:
        now = monotonic()
        with self._lock:
            self._windows = {
                key: value for key, value in self._windows.items() if now - value[0] < 60
            }
            start, count = self._windows.get(actor, (now, 0))
            if count >= 30 or (actor not in self._windows and len(self._windows) >= 1024):
                raise TooManyRequestsError("查看照片过于频繁，请稍后重试")
            self._windows[actor] = (start, count + 1)
