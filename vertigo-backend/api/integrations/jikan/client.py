# integrations.jikan.client

from flask import g
import requests
from requests import Session

JIKAN_BASE = "https://api.jikan.moe/v4"
TIMEOUT = 10

class JikanSession:
    def __init__(self, base_url=JIKAN_BASE, user_agent="Vertigo/Jikan"):
        self.base_url = base_url
        self.session = Session()
        self.session.headers.update({"User-Agent": user_agent})

    def _get(self, path, params=None):
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params or {}, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json().get("data")

    def search_manga(self, query):
        return self._get("/manga", {"q": query})

    def manga(self, mal_id):
        return self._get(f"/manga/{mal_id}")

    def manga_characters(self, mal_id):
        return self._get(f"/manga/{mal_id}/characters")

    def character(self, mal_id):
        return self._get(f"/characters/{mal_id}")

    def person(self, mal_id):
        return self._get(f"/people/{mal_id}")

    def magazine(self, mal_id):
        return self._get(f"/magazines/{mal_id}")


def get_jikan_session():
    if "jikan_session" in g:
        return g.jikan_session

    # no auth required for jikan, but kept symmetrical
    g.jikan_session = JikanSession()
    return g.jikan_session


