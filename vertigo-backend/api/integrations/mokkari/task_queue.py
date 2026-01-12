import queue
import threading
from api.integrations.mokkari.mokkari_rate_limiter import wait_for_mokkari_slot

_mokkari_queue = queue.Queue(maxsize=500)
_workers_started = False
_workers_lock = threading.Lock()


def _mokkari_worker(app):
    with app.app_context():
        while True:
            task = _mokkari_queue.get()

            if task is None:
                break

            func, args, kwargs = task

            try:
                wait_for_mokkari_slot()
                func(*args, **kwargs)
            except Exception:
                app.logger.exception("Mokkari task failed")
            finally:
                _mokkari_queue.task_done()


def start_mokkari_workers(app, num_workers=1):
    global _workers_started

    with _workers_lock:
        if _workers_started:
            return

        for i in range(num_workers):
            t = threading.Thread(
                target=_mokkari_worker,
                args=(app,),
                name=f"mokkari-worker-{i}",
                daemon=True,
            )
            t.start()

        _workers_started = True


def submit_mokkari_task(func, *args, **kwargs):
    try:
        _mokkari_queue.put_nowait((func, args, kwargs))
    except queue.Full:
        from flask import current_app
        current_app.logger.warning(
            "Mokkari queue full – dropping enrichment task"
        )
