from flask import g, current_app
from mokkari.session import Session
from mokkari.sqlite_cache import SqliteCache
from mokkari.exceptions import CacheError

_mokkari_cache: SqliteCache | None = None

def get_mokkari_cache():
    """Return a cache instance."""
    cache_path = current_app.config.get("METRON_CACHE_DB")
    if not cache_path:
        return None
    # Each call creates a new SqliteCache instance (thread-safe)
    return SqliteCache(cache_path)


def get_mokkari_session():
    if "mokkari_session" in g:
        return g.mokkari_session

    username = current_app.config.get("METRON_USERNAME")
    password = current_app.config.get("METRON_PASSWORD")

    if not username or not password:
        g.mokkari_session = None
        return None

    cache = get_mokkari_cache() 
    g.mokkari_session = Session(
        username=username,
        passwd=password,
        cache=cache,
        user_agent="Vertigo/Metron",
        dev_mode=current_app.config.get("METRON_DEV_MODE", False),
    )

    return g.mokkari_session
