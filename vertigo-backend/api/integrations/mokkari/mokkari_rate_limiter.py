import re
import threading
import time

from flask import current_app

_lock = threading.Lock()
_next_allowed_ts = 0.0  # monotonic timestamp

_UNIT_SECONDS = {"hour": 3600, "minute": 60, "second": 1}


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


def note_rate_limit(retry_after: int | None) -> None:
    """Push every later caller back until Metron will talk to us again, without sleeping."""
    global _next_allowed_ts

    if not retry_after:
        return
    with _lock:
        _next_allowed_ts = max(_next_allowed_ts, time.monotonic() + retry_after)


def retry_after_seconds(exc, default: int | None = None) -> int | None:

    resp = getattr(getattr(exc, "__cause__", None), "response", None)
    header = resp.headers.get("Retry-After") if resp is not None else None
    if header is not None:
        try:
            return max(1, int(float(header)))
        except (TypeError, ValueError):
            pass

    total = 0
    found = False
    for amount, unit in re.findall(r"(\d+)\s*(hour|minute|second)", str(exc)):
        found = True
        total += int(amount) * _UNIT_SECONDS[unit]
    return max(1, total) if found else default
