import queue
import threading
from api.integrations.jikan.rate_limiter import wait_for_jikan_slot

_jikan_queue = queue.Queue(maxsize=500)
_workers_started = False
_workers_lock = threading.Lock()


def _jikan_worker(app):
    with app.app_context():
        while True:
            task = _jikan_queue.get()

            if task is None:
                break

            func, args, kwargs = task

            try:
                wait_for_jikan_slot()
                func(*args, **kwargs)
            except Exception:
                app.logger.exception("Jikan task failed")
            finally:
                _jikan_queue.task_done()


def start_jikan_workers(app, num_workers=1):
    global _workers_started

    with _workers_lock:
        if _workers_started:
            return

        for i in range(num_workers):
            t = threading.Thread(
                target=_jikan_worker,
                args=(app,),
                name=f"jikan-worker-{i}",
                daemon=True,
            )
            t.start()

        _workers_started = True


def submit_jikan_task(func, *args, **kwargs):
    try:
        _jikan_queue.put_nowait((func, args, kwargs))
    except queue.Full:
        from flask import current_app
        current_app.logger.warning(
            "Jikan queue full – dropping enrichment task"
        )
