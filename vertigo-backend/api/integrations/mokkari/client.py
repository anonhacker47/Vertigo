import threading

from flask import current_app
from mokkari.exceptions import CacheError
from mokkari.rate_limit import HeaderPacedRateLimiter
from mokkari.session import Session
from mokkari.sqlite_cache import SqliteCache

from api.integrations.mokkari.credentials import resolve_metron_token
from api.utils.auth import token_auth

USER_AGENT = "Vertigo/Metron"

_lock = threading.RLock()
_cache = None
_cache_path = None
_sessions: dict[str, Session] = {}


def get_mokkari_cache():
    global _cache, _cache_path

    path = current_app.config.get("METRON_CACHE_DB")
    if not path:
        return None

    with _lock:
        if _cache is None or _cache_path != path:
            try:
                _cache = SqliteCache(path)
                _cache_path = path
            except CacheError as e:
                current_app.logger.warning("Metron cache unavailable (%s): %s", path, e)
                return None
        return _cache


def _build_session(token, cache):
    return Session(
        api_token=token,
        cache=cache,
        user_agent=USER_AGENT,
        dev_mode=bool(current_app.config.get("METRON_DEV_MODE")),
        rate_limiter=HeaderPacedRateLimiter(),
    )


def session_for_token(token):
    with _lock:
        session = _sessions.get(token)
        if session is None:
            session = _build_session(token, get_mokkari_cache())
            _sessions[token] = session
        return session


def forget_session(token):
    if not token:
        return
    with _lock:
        session = _sessions.pop(token, None)
    if session is not None:
        session.close()


def verification_session(token):
    """Cache-less: a cached hit never reaches Metron, so it can't vouch for a token."""
    return Session(api_token=token, cache=None, user_agent=USER_AGENT,
                   dev_mode=bool(current_app.config.get("METRON_DEV_MODE")))


def get_mokkari_session(user=None):
    """Session for ``user`` (default: the request's user), or None without a token."""
    if user is None:
        user = token_auth.current_user()
    token, _ = resolve_metron_token(user)
    if not token:
        return None
    return session_for_token(token)
