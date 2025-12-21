from flask import g, current_app
from mokkari.session import Session
from mokkari.sqlite_cache import SqliteCache
from mokkari.exceptions import CacheError


def get_mokkari_cache():
    if "mokkari_cache" in g:
        return g.mokkari_cache

    cache_path = current_app.config.get("METRON_CACHE_DB")
    if not cache_path:
        g.mokkari_cache = None
        return None

    try:
        g.mokkari_cache = SqliteCache(cache_path)
        return g.mokkari_cache
    except CacheError:
        g.mokkari_cache = None
        return None


def get_mokkari_session():
    if "mokkari_session" in g:
        return g.mokkari_session

    username = current_app.config.get("METRON_USERNAME")
    password = current_app.config.get("METRON_PASSWORD")

    if not username or not password:
        g.mokkari_session = None
        return None

    g.mokkari_session = Session(
        username=username,
        passwd=password,
        cache=get_mokkari_cache(),
        user_agent="Vertigo/Metron",
        dev_mode=current_app.config.get("METRON_DEV_MODE", False),
    )

    return g.mokkari_session
