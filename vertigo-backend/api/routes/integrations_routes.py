import re

from flask import Blueprint, current_app
from apifairy import authenticate, body
from marshmallow import Schema, fields, validate
from mokkari.exceptions import ApiError, RateLimitError

from api import db
from api.integrations.mokkari.client import forget_session
from api.integrations.mokkari.credentials import USER_TOKEN, resolve_metron_token
from api.integrations.mokkari.status import (
    MetronAuthError, check_token, metron_status, retry_after_seconds,
)
from api.integrations.tenrai.status import tenrai_status
from api.utils.auth import token_auth

integrations = Blueprint('integrations', __name__)

TOKEN_RE = re.compile(r"[\x21-\x7e]{8,255}")

TOKEN_INVALID = "Tokens contain only letters, digits and punctuation, with no spaces."
TOKEN_REJECTED = "Metron rejected this token. Check it was copied in full."
SERVER_TOKEN_REJECTED = "Metron rejected the server's token. Ask the server admin to update it."
NOT_CONFIGURED = "No Metron API token is set for this account or server."


class MetronTokenSchema(Schema):
    api_token = fields.String(required=True, validate=validate.Length(max=255))


def _status(user):
    return {"metron": metron_status(user), "myanimelist": tenrai_status()}


def _rate_limited(e):
    retry_after = retry_after_seconds(e)
    current_app.logger.warning("Metron rate limited while checking a token: %s", e)
    return {"error": "rate_limited", "retry_after": retry_after, "message": str(e)}, 429


def _unreachable(e):
    current_app.logger.warning("Metron token check failed: %s", e)
    return {"error": "metron_error", "message": "Couldn't reach Metron. Try again shortly."}, 502


@integrations.route('/integrations', methods=['GET'])
@authenticate(token_auth)
def get_status():
    """Which external sources are connected for the authenticated user"""
    return _status(token_auth.current_user())


@integrations.route('/integrations/metron', methods=['PUT'])
@authenticate(token_auth)
@body(MetronTokenSchema)
def save_metron_token(args):
    """Store the user's Metron API token after checking it against Metron"""
    user = token_auth.current_user()
    token = args["api_token"].strip()
    if not TOKEN_RE.fullmatch(token):
        return {"error": "invalid_token", "message": TOKEN_INVALID}, 400

    try:
        rate_limit = check_token(token)
    except MetronAuthError:
        return {"error": "token_rejected", "source": USER_TOKEN, "message": TOKEN_REJECTED}, 400
    except RateLimitError as e:
        return _rate_limited(e)
    except ApiError as e:
        return _unreachable(e)

    previous = user.metron_api_token
    user.metron_api_token = token
    db.session.commit()
    if previous and previous != token:
        forget_session(previous)

    status = _status(user)
    status["metron"]["rate_limit"] = rate_limit or status["metron"]["rate_limit"]
    return status


@integrations.route('/integrations/metron', methods=['DELETE'])
@authenticate(token_auth)
def clear_metron_token():
    """Forget the user's own Metron token (the server token, if any, applies again)"""
    user = token_auth.current_user()
    previous = user.metron_api_token
    user.metron_api_token = None
    db.session.commit()
    forget_session(previous)
    return _status(user)


@integrations.route('/integrations/metron/test', methods=['POST'])
@authenticate(token_auth)
def test_metron():
    """Check the token currently in effect against Metron"""
    user = token_auth.current_user()
    token, source = resolve_metron_token(user)
    if not token:
        return {"error": "not_configured", "message": NOT_CONFIGURED}, 503

    try:
        rate_limit = check_token(token)
    except MetronAuthError:
        message = TOKEN_REJECTED if source == USER_TOKEN else SERVER_TOKEN_REJECTED
        return {"error": "token_rejected", "source": source, "message": message}, 400
    except RateLimitError as e:
        return _rate_limited(e)
    except ApiError as e:
        return _unreachable(e)

    return {"ok": True, "source": source, "rate_limit": rate_limit}
