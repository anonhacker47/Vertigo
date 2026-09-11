from flask import current_app
import requests

from api.integrations.tenrai.client import get_tenrai_session
from api.integrations.tenrai.rate_limiter import wait_for_tenrai_slot


def _retry_after_seconds(resp, attempt):
    """Honour Tenrai's Retry-After header, falling back to a small backoff."""
    header = resp.headers.get("Retry-After") if resp is not None else None
    try:
        return max(1, int(float(header)))
    except (TypeError, ValueError):
        return attempt * 2 + 2


def fetch_tenrai_entity_info(
    entity_type: str,
    mal_id: int,
    *,
    max_retries: int = 2,
):
    """Return the raw Tenrai payload for a creator or character, or None.

    Publishers are MAL magazines. Tenrai only lists magazines (id, name, url)
    and has no per-magazine endpoint, so there is no description or image to
    fetch for them and the request is skipped entirely.
    """
    if not mal_id:
        return None

    fetch = {
        "creator": lambda s: s.person(mal_id),
        "character": lambda s: s.character(mal_id),
    }.get(entity_type)
    if fetch is None:
        return None

    session = get_tenrai_session()
    if not session:
        return None

    for attempt in range(max_retries + 1):
        try:
            wait_for_tenrai_slot()
            return fetch(session)

        except requests.exceptions.HTTPError as e:
            resp = e.response
            status = resp.status_code if resp is not None else None

            if status != 429:
                current_app.logger.warning(
                    "Tenrai fetch failed (%s:%s) -> %s", entity_type, mal_id, e
                )
                return None

            if attempt >= max_retries:
                current_app.logger.warning(
                    "Tenrai rate limit exceeded (%s:%s), giving up", entity_type, mal_id
                )
                return None

            retry_after = _retry_after_seconds(resp, attempt)
            current_app.logger.info(
                "Tenrai rate limited (%s:%s), retrying in %ss",
                entity_type, mal_id, retry_after,
            )
            wait_for_tenrai_slot(retry_after)

        except Exception as e:
            current_app.logger.warning(
                "Tenrai fetch failed (%s:%s) -> %s", entity_type, mal_id, e
            )
            return None

    return None
