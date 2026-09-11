import time
import threading

_lock = threading.Lock()
_next_allowed_ts = 0.0

MIN_INTERVAL_SECONDS = 0.6


def wait_for_tenrai_slot(retry_after: int | float | None = None):
    """Block until the next Tenrai request slot, then reserve it.

    Passing ``retry_after`` pushes the next slot out by that many seconds
    instead of the default interval (used after a 429).
    """
    global _next_allowed_ts

    with _lock:
        now = time.monotonic()

        if _next_allowed_ts > now:
            time.sleep(_next_allowed_ts - now)

        if retry_after:
            _next_allowed_ts = time.monotonic() + retry_after
        else:
            _next_allowed_ts = time.monotonic() + MIN_INTERVAL_SECONDS
