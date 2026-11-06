"""One process-wide capacity owner for generation and decision requests."""

from threading import BoundedSemaphore

REQUEST_SLOTS = BoundedSemaphore(2)
