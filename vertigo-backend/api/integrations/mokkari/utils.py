from flask import current_app
from api.integrations.mokkari.client import get_mokkari_session
from api.integrations.mokkari.mokkari_rate_limiter import wait_for_mokkari_slot
from mokkari.exceptions import RateLimitError

def fetch_metron_entity_info(
    entity_type: str,
    entity_id: int,
    *,
    max_retries: int = 2,
):
    if not entity_id:
        return None

    session = get_mokkari_session()
    if not session:
        return None

    for attempt in range(max_retries + 1):
        try:
            wait_for_mokkari_slot()
            
            if entity_type == "creator":
                return session.creator(entity_id)
            elif entity_type == "publisher":
                return session.publisher(entity_id)
            elif entity_type == "character":
                return session.character(entity_id)
            else:
                return None

        except RateLimitError as e:
            if attempt >= max_retries:
                current_app.logger.warning(
                    f"Metron rate limit exceeded "
                    f"({entity_type}:{entity_id}), giving up"
                )
                return None

            retry_after = max(1, int(getattr(e, "retry_after", 40)))

            current_app.logger.info(
                f"Metron rate limited "
                f"({entity_type}:{entity_id}), retrying in {retry_after}s"
            )

            wait_for_mokkari_slot(retry_after)

        except Exception as e:
            current_app.logger.warning(
                f"Metron fetch failed "
                f"({entity_type}:{entity_id}) → {e}"
            )
            return None

    return None