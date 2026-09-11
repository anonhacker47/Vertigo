import time

from flask import current_app, g
import requests
from requests import Session

TENRAI_BASE = "https://api.tenrai.org/v1"
TIMEOUT = 10

RETRYABLE_STATUSES = {500, 502, 503, 504}
MAX_RETRIES = 1
RETRY_BACKOFF_SECONDS = 1.5


class TenraiSession:
    def __init__(self, base_url=TENRAI_BASE, user_agent="Vertigo/Tenrai", server_key=None):
        self.base_url = base_url
        self.session = Session()
        self.session.headers.update({"User-Agent": user_agent})

    def _get(self, path, params=None):
        url = f"{self.base_url}{path}"

        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = self.session.get(url, params=params or {}, timeout=TIMEOUT)
                resp.raise_for_status()
                return resp.json().get("data")

            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else None
                if status not in RETRYABLE_STATUSES or attempt >= MAX_RETRIES:
                    raise

            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError):
                if attempt >= MAX_RETRIES:
                    raise

            time.sleep(RETRY_BACKOFF_SECONDS)

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


def get_tenrai_session():
    if "tenrai_session" in g:
        return g.tenrai_session

    g.tenrai_session = TenraiSession(
        server_key=current_app.config.get("TENRAI_SERVER_KEY") or None,
    )
    return g.tenrai_session
