"""Checks a token against Metron and builds what the Settings page shows."""
import math

from mokkari.exceptions import ApiError

from api.integrations.mokkari.client import session_for_token, verification_session
from api.integrations.mokkari.credentials import (
    USER_TOKEN, mask_token, resolve_metron_token, server_token,
)

AUTH_FAILURE_STATUSES = (401, 403)


class MetronAuthError(Exception):
    """Metron rejected the token."""


def retry_after_seconds(exc):
    """Whole seconds to wait, or None when the error carries no wait."""
    retry_after = getattr(exc, "retry_after", None)
    if not retry_after or retry_after <= 0:
        return None
    return max(1, math.ceil(retry_after))


def _window(window):
    return {
        "limit": window.limit,
        "remaining": window.remaining,
        "reset": window.reset.isoformat() if window.reset else None,
    }


def rate_limit_dict(status):
    if status is None:
        return None
    if status.burst.limit is None and status.sustained.limit is None:
        return None
    return {"burst": _window(status.burst), "sustained": _window(status.sustained)}


def _upstream_status(exc):
    resp = getattr(getattr(exc, "__cause__", None), "response", None)
    return getattr(resp, "status_code", None)


def check_token(token):
    """One uncached request with ``token``; returns the rate-limit windows.

    Raises ``MetronAuthError`` on 401/403. Other errors pass through.
    """
    with verification_session(token) as session:
        try:
            session.series_type_list()
        except ApiError as e:
            if _upstream_status(e) in AUTH_FAILURE_STATUSES:
                raise MetronAuthError(str(e)) from e
            raise
        return rate_limit_dict(session.rate_limit_status)


def metron_status(user):
    token, source = resolve_metron_token(user)
    status = {
        "configured": token is not None,
        "source": source,
        "token_hint": mask_token(token) if source == USER_TOKEN else None,
        "server_token": server_token() is not None,
        "rate_limit": None,
    }
    if token:
        status["rate_limit"] = rate_limit_dict(session_for_token(token).rate_limit_status)
    return status
