"""Progress of a restore on the media worker; finished runs stay an hour. TRANSFER_RUN_INLINE runs them in the request (tests)."""
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from flask import current_app

from api import db, media
from api.jobs import registry as jobs
from api.transfer.errors import TransferError

KEEP_FOR = timedelta(hours=1)
MAX_PER_USER = 20


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z') if dt else None


@dataclass
class Run:
    id: str
    user_id: int
    kind: str                      # restore
    label: str
    status: str = 'queued'         # queued | running | done | failed
    total: int = 0
    done: int = 0
    created_at: datetime = field(default_factory=_now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    summary: dict = field(default_factory=dict)
    error: Optional[str] = None
    work: Optional[Callable] = field(default=None, repr=False, compare=False)
    cleanup: Optional[Callable] = field(default=None, repr=False, compare=False)

    @property
    def finished(self) -> bool:
        return self.status in ('done', 'failed')

    def to_dict(self) -> dict:
        return {
            'id': self.id, 'kind': self.kind, 'label': self.label, 'status': self.status,
            'total': self.total, 'done': min(self.done, self.total) if self.total else self.done,
            'summary': self.summary, 'error': self.error,
            'created_at': _iso(self.created_at), 'started_at': _iso(self.started_at),
            'finished_at': _iso(self.finished_at),
        }


_runs: dict = {}
_lock = threading.Lock()


def create(kind: str, label: str, user_id: int, work: Callable, total: int = 0,
           cleanup: Optional[Callable] = None) -> Run:
    """Register the work; ``work(run)`` returns the summary dict when it is done."""
    run = Run(id=uuid.uuid4().hex, kind=kind, label=label, user_id=user_id, total=total,
              work=work, cleanup=cleanup)
    with _lock:
        _prune(user_id)
        _runs[run.id] = run
    return run


def get(run_id: str, user_id: int) -> Optional[Run]:
    run = _runs.get(run_id)
    return run if run is not None and run.user_id == user_id else None


def start(run: Run) -> bool:
    """Queue the run (or do it now under ``TRANSFER_RUN_INLINE``); False when the queue refused it."""
    if current_app.config.get('TRANSFER_RUN_INLINE'):
        execute(run.id)
        return True
    job = jobs.submit(media.submit, run.kind, run.label, run.user_id, execute, run.id, queue='media')
    if job is None:
        _finish(run, 'failed', error='The server is busy right now; try again in a moment.')
        return False
    return True


def execute(run_id: str) -> None:
    """Worker entry point."""
    run = _runs.get(run_id)
    if run is None or run.work is None:
        return
    with _lock:
        run.status = 'running'
        run.started_at = _now()
    try:
        summary = run.work(run)
        _finish(run, 'done', summary=summary if summary is not None else run.summary)
    except TransferError as exc:
        db.session.rollback()
        _finish(run, 'failed', error=str(exc))
    except Exception:
        db.session.rollback()
        current_app.logger.exception('%s run %s failed', run.kind, run.id)
        _finish(run, 'failed', error='Something went wrong on the server; the log has the details.')
    finally:
        db.session.close()


def reset() -> None:
    with _lock:
        _runs.clear()


def _finish(run: Run, status: str, summary: Optional[dict] = None, error: Optional[str] = None) -> None:
    with _lock:
        run.status = status
        if summary is not None:
            run.summary = summary
        run.error = error
        run.finished_at = _now()
        if status == 'done':
            run.done = run.total
        cleanup, run.work, run.cleanup = run.cleanup, None, None
    if cleanup is not None:
        try:
            cleanup()
        except Exception:  # pragma: no cover
            current_app.logger.exception('cleanup after %s run %s failed', run.kind, run.id)


def _prune(user_id: int) -> None:
    """Drop finished runs older than ``KEEP_FOR`` and all but the newest ``MAX_PER_USER`` of a user's."""
    cutoff = _now() - KEEP_FOR
    for run_id, run in list(_runs.items()):
        if run.finished and run.finished_at and run.finished_at < cutoff:
            del _runs[run_id]
    mine = sorted((r for r in _runs.values() if r.user_id == user_id and r.finished),
                  key=lambda r: r.created_at)
    for run in mine[:max(0, len(mine) - (MAX_PER_USER - 1))]:
        _runs.pop(run.id, None)
