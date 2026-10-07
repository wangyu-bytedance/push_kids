"""Bound blocking stage I/O without waiting for a stuck executor on loop shutdown."""

import asyncio
import threading
from collections.abc import Callable
from contextlib import suppress
from time import monotonic
from typing import TypeVar

from push_kids.agent_processing.failures import StageFailure

T = TypeVar("T")
_IO_SLOTS = threading.BoundedSemaphore(4)


async def stage_io(operation: Callable[[], T], deadline: float) -> T:
    loop = asyncio.get_running_loop()
    result: asyncio.Future[T] = loop.create_future()

    def finish(value: T | None, error: BaseException | None) -> None:
        if result.done():
            return
        if error is not None:
            result.set_exception(error)
        else:
            result.set_result(value)  # type: ignore[arg-type]

    def run() -> None:
        value, error = None, None
        try:
            if monotonic() >= deadline:
                raise StageFailure("local_deadline")
            value = operation()
        except BaseException as exc:
            error = exc
        finally:
            _IO_SLOTS.release()
        with suppress(RuntimeError):
            loop.call_soon_threadsafe(finish, value, error)

    try:
        async with asyncio.timeout(max(0, deadline - monotonic())):
            while not _IO_SLOTS.acquire(blocking=False):
                await asyncio.sleep(0.01)
            if monotonic() >= deadline:
                _IO_SLOTS.release()
                raise StageFailure("local_deadline")
            threading.Thread(target=run, daemon=True, name="analysis-stage-io").start()
            return await result
    except TimeoutError:
        raise StageFailure("local_deadline") from None
