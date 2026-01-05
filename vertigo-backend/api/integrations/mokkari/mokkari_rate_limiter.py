
import time
import threading
from flask import current_app

_lock = threading.Lock()
_next_allowed_ts = 0.0  # monotonic timestamp


def wait_for_mokkari_slot(retry_after: int | None = None):
    """
    Global rate-limit for Mokkari requests.
    """

    global _next_allowed_ts

    with _lock:
        now = time.monotonic()

        if _next_allowed_ts > now:
            sleep_for = _next_allowed_ts - now
            current_app.logger.debug(
                f"Mokkari global wait: {sleep_for:.1f}s"
            )
            time.sleep(sleep_for)

        if retry_after:
            _next_allowed_ts = time.monotonic() + retry_after
        else:
            _next_allowed_ts = time.monotonic() + 2