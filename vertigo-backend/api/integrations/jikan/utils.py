from flask import current_app
from api.integrations.jikan.client import get_jikan_session
from api.integrations.jikan.rate_limiter import wait_for_jikan_slot
import requests

def fetch_jikan_entity_info(
    entity_type: str,
    mal_id: int,
    *,
    max_retries: int = 2,
):
    if not mal_id:
        return None

    session = get_jikan_session()
    if not session:
        return None

    for attempt in range(max_retries + 1):
        try:
            wait_for_jikan_slot()
            
            if entity_type == "creator":
                return session.person(mal_id)
            elif entity_type == "publisher":
                return session.magazine(mal_id)
            elif entity_type == "character":
                return session.character(mal_id)
            else:
                return None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if attempt >= max_retries:
                    current_app.logger.warning(
                        f"Jikan rate limit exceeded "
                        f"({entity_type}:{mal_id}), giving up"
                    )
                    return None

                retry_after = attempt * 2 + 2 

                current_app.logger.info(
                    f"Jikan rate limited "
                    f"({entity_type}:{mal_id}), retrying in {retry_after}s"
                )

                wait_for_jikan_slot(retry_after)
            else:
                current_app.logger.warning(
                    f"Jikan fetch failed "
                    f"({entity_type}:{mal_id}) → {e}"
                )
                return None

        except Exception as e:
            current_app.logger.warning(
                f"Jikan fetch failed "
                f"({entity_type}:{mal_id}) → {e}"
            )
            return None

    return None
