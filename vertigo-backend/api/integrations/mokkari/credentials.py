"""Which Metron API token applies: the user's own, else the server's."""
from flask import current_app

USER_TOKEN = "user"
SERVER_TOKEN = "server"


def server_token():
    return (current_app.config.get("METRON_API_TOKEN") or "").strip() or None


def resolve_metron_token(user=None):
    """Return ``(token, source)``; ``source`` is ``"user"``, ``"server"`` or ``None``."""
    token = (getattr(user, "metron_api_token", None) or "").strip()
    if token:
        return token, USER_TOKEN
    token = server_token()
    if token:
        return token, SERVER_TOKEN
    return None, None


def mask_token(token):
    if not token:
        return None
    tail = token[-4:] if len(token) > 8 else ""
    return f"••••{tail}"
