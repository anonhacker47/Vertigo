import time

from flask import current_app
from mokkari.exceptions import RateLimitError

from api.integrations.mokkari.client import get_mokkari_session
from api.integrations.mokkari.status import retry_after_seconds

MAX_RETRY_WAIT_SECONDS = 90

_FETCHERS = {
    "creator": lambda session, _id: session.creator(_id),
    "publisher": lambda session, _id: session.publisher(_id),
    "character": lambda session, _id: session.character(_id),
}


def fetch_metron_entity_info(entity_type, entity_id, user=None, *, max_retries=2):
    """Creator, publisher or character from Metron, or None.

    ``user`` picks the token; background tasks must pass it.
    """
    if not entity_id:
        return None

    fetch = _FETCHERS.get(entity_type)
    if fetch is None:
        return None

    session = get_mokkari_session(user)
    if not session:
        return None

    for attempt in range(max_retries + 1):
        try:
            return fetch(session, entity_id)

        except RateLimitError as e:
            wait = retry_after_seconds(e) or 5
            if attempt >= max_retries or wait > MAX_RETRY_WAIT_SECONDS:
                current_app.logger.warning(
                    "Metron rate limit exceeded (%s:%s), giving up: %s",
                    entity_type, entity_id, e)
                return None
            current_app.logger.info(
                "Metron rate limited (%s:%s), retrying in %ss", entity_type, entity_id, wait)
            time.sleep(wait)

        except Exception as e:
            current_app.logger.warning(
                "Metron fetch failed (%s:%s) -> %s", entity_type, entity_id, e)
            return None

    return None
