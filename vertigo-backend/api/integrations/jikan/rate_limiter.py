import time
import threading
from flask import current_app

_lock = threading.Lock()
_next_allowed_ts = 0.0 

def wait_for_jikan_slot(retry_after: int | float | None = None):
    
    global _next_allowed_ts

    with _lock:
        now = time.monotonic()

        if _next_allowed_ts > now:
            sleep_for = _next_allowed_ts - now
            time.sleep(sleep_for)

        if retry_after:
            _next_allowed_ts = time.monotonic() + retry_after
        else:
            _next_allowed_ts = time.monotonic() + 1.1
