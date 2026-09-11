import queue
import threading
from api.integrations.tenrai.rate_limiter import wait_for_tenrai_slot

_tenrai_queue = queue.Queue(maxsize=500)
_workers_started = False
_workers_lock = threading.Lock()


def _tenrai_worker(app):
    with app.app_context():
        while True:
            task = _tenrai_queue.get()

            if task is None:
                break

            func, args, kwargs = task

            try:
                wait_for_tenrai_slot()
                func(*args, **kwargs)
            except Exception:
                app.logger.exception("Tenrai task failed")
            finally:
                _tenrai_queue.task_done()


def start_tenrai_workers(app, num_workers=1):
    global _workers_started

    with _workers_lock:
        if _workers_started:
            return

        for i in range(num_workers):
            t = threading.Thread(
                target=_tenrai_worker,
                args=(app,),
                name=f"tenrai-worker-{i}",
                daemon=True,
            )
            t.start()

        _workers_started = True


def submit_tenrai_task(func, *args, **kwargs):
    try:
        _tenrai_queue.put_nowait((func, args, kwargs))
    except queue.Full:
        from flask import current_app
        current_app.logger.warning(
            "Tenrai queue full – dropping enrichment task"
        )
