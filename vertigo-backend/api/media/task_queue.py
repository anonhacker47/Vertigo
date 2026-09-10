import queue
import threading

from flask import current_app

_queue: "queue.Queue" = queue.Queue(maxsize=2000)
_worker_started = False
_worker_lock = threading.Lock()

def _worker(app):
    with app.app_context():
        while True:
            task = _queue.get()
            if task is None:
                break
            func, args, kwargs = task
            try:
                func(*args, **kwargs)
            except Exception:
                app.logger.exception("media task failed")
            finally:
                _queue.task_done()


def start_media_worker(app, num_workers: int = 2) -> None:
    """Start the workers once per process (called from create_app)."""
    global _worker_started
    with _worker_lock:
        if _worker_started:
            return
        for i in range(num_workers):
            threading.Thread(target=_worker, args=(app,), name=f"media-worker-{i}",
                             daemon=True).start()
        _worker_started = True


def submit(func, *args, **kwargs) -> bool:
    """Queue func(*args, **kwargs) to run on a media worker with an app context."""
    try:
        _queue.put_nowait((func, args, kwargs))
        return True
    except queue.Full:
        current_app.logger.warning("media queue full, dropping task %s", func.__name__)
        return False
