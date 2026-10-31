"""Background work that is queued or running right now.

A job wraps the function a worker queue runs so it can be listed while pending. It is
forgotten as soon as it finishes, however it went; failures reach the log via the worker.
"""
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z') if dt else None


@dataclass
class Job:
    id: str
    kind: str
    label: str
    user_id: int
    queue: str
    status: str = 'queued'
    queued_at: datetime = field(default_factory=_now)
    started_at: Optional[datetime] = None
    func: Optional[Callable] = field(default=None, repr=False, compare=False)
    args: tuple = field(default=(), repr=False, compare=False)
    kwargs: dict = field(default_factory=dict, repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id, 'kind': self.kind, 'label': self.label, 'queue': self.queue,
            'status': self.status, 'queued_at': _iso(self.queued_at), 'started_at': _iso(self.started_at),
        }


_jobs: dict[str, Job] = {}
_lock = threading.Lock()


def submit(via, kind, label, user_id, func, *args, queue='media', **kwargs) -> Optional[Job]:
    """List a job and hand it to ``via``, a queue's submit function. A refused job is unlisted again."""
    job = Job(id=uuid.uuid4().hex, kind=kind, label=label, user_id=user_id, queue=queue,
              func=func, args=args, kwargs=kwargs)
    with _lock:
        _jobs[job.id] = job
    if via(run, job.id) is False:
        _forget(job.id)
        return None
    return job


def run(job_id: str) -> None:
    """Worker entry point: run the job's function, then drop it from the list."""
    job = _jobs.get(job_id)
    if job is None or job.func is None:
        return
    with _lock:
        job.status = 'running'
        job.started_at = _now()
    try:
        job.func(*job.args, **job.kwargs)
    finally:
        _forget(job_id)


def for_user(user_id: int) -> list[Job]:
    """Pending jobs, running first, then oldest waiting first."""
    with _lock:
        rows = [j for j in _jobs.values() if j.user_id == user_id]
    return sorted(rows, key=lambda j: (j.status != 'running', j.queued_at))


def reset() -> None:
    with _lock:
        _jobs.clear()


def _forget(job_id: str) -> None:
    with _lock:
        _jobs.pop(job_id, None)
