import re

from flask import Blueprint, current_app
from apifairy import authenticate, arguments
from marshmallow import Schema, fields
from mokkari.exceptions import RateLimitError, ApiError

from api.integrations.mokkari.mokkari_rate_limiter import (
    wait_for_mokkari_slot, note_rate_limit, retry_after_seconds,
)
from api.integrations.mokkari.client import get_mokkari_session
from api.utils.auth import token_auth

mokkari = Blueprint('mokkari', __name__, url_prefix="/api")

#avoid fetching entity list from all issues.
ENTITY_SAMPLE_ISSUES = 10

def _rate_limited(e: RateLimitError):
    retry_after = retry_after_seconds(e)
    note_rate_limit(retry_after)
    current_app.logger.warning("Metron rate limited: %s", e)
    return {"error": "rate_limited", "retry_after": retry_after, "message": str(e)}, 429


def _issue_url(series_url: str | None, number) -> str | None:
    if not series_url or number in (None, ""):
        return None
    slug = series_url.rstrip("/").rsplit("/", 1)[-1]
    num = re.sub(r"[^\w\s-]", "", str(number)).strip().lower()
    num = re.sub(r"[-\s]+", "-", num)
    if not slug or not num:
        return None
    return f"https://metron.cloud/issue/{slug}-{num}/"

class SearchQuerySchema(Schema):
    query = fields.Str(required=True)

@mokkari.route("/metron/series/search", methods=["GET"])
@arguments(SearchQuerySchema, location="query")
@authenticate(token_auth)
def search_series(args):
    query = args["query"]
    session = get_mokkari_session()

    try:
        wait_for_mokkari_slot()
        series_list = session.series_list({"name": query})
        items = []

        for s in series_list:

            items.append({
                "metron_id": s.id,
                "name": s.display_name,
                "year_began": s.year_began,
                "issue_count": s.issue_count,
                "volume": s.volume,
            })

        return {
            "items": items,
            "total_found": len(series_list)
        }

    except RateLimitError as e:
        return _rate_limited(e)
    except ApiError as e:
        return {"error": "metron_error", "message": str(e)}, 502


@mokkari.route("/metron/series/<int:series_id>", methods=["GET"])
@authenticate(token_auth)
def get_series_detail(series_id):
    session = get_mokkari_session()
    if not session:
        return {"error": "no_session"}, 500

    try:
        wait_for_mokkari_slot()
        series = session.series(series_id)

        issues = session.issues_list({"series_id": series_id, "number": "1"})
        first_issue_image = str(issues[0].image) if issues else None

        return {
            "metron_id": series.id,
            "name": series.name,
            "volume": series.volume,
            "year_began": series.year_began,
            "year_end": getattr(series, "year_end", None),
            "issue_count": series.issue_count,
            "status": getattr(series, "status", None),
            "publisher": {
                "metron_id": getattr(series.publisher, "id", None) if getattr(series, "publisher", None) else None,
                        "value": getattr(series.publisher, "name", None) if getattr(series, "publisher", None) else None,
            },
            "desc": getattr(series, "desc", None),
            "genres": [ 
                { "metron_id": getattr(g, "name", None),
                   "value": getattr(g, "name", None),
                }
                for g in getattr(series, "genres", []) or []
            ],
            "metron_url": str(getattr(series, "resource_url", None)) if getattr(series, "resource_url", None) else None,
            "image_first_issue": first_issue_image
        }

    except RateLimitError as e:
        return _rate_limited(e)
    except ApiError as e:
        return {"error": "metron_error", "message": str(e)}, 502
    

@mokkari.route("/metron/series/<int:series_id>/entities", methods=["GET"])
@authenticate(token_auth)
def get_series_entities(series_id):
    """Issue list plus the creators and characters seen in the first few issues"""
    session = get_mokkari_session()

    if not session:
        return {"error": "no_session"}, 500

    try:
        wait_for_mokkari_slot()
        series = session.series(series_id)
        issue_stubs = session.issues_list({"series_id": series_id})
    except RateLimitError as e:
        return _rate_limited(e)
    except ApiError as e:
        return {"error": "metron_error", "message": str(e)}, 502

    series_url = str(series.resource_url) if getattr(series, "resource_url", None) else None
    issues = {}
    for stub in issue_stubs:
        issues[stub.id] = {
            "metron_id": stub.id,
            "number": getattr(stub, "number", None),
            "metron_url": _issue_url(series_url, getattr(stub, "number", None)),
            "image": str(stub.image) if getattr(stub, "image", None) else None,
        }

    creators = {}
    characters = {}
    sampled = 0
    partial = False
    retry_after = None

    for stub in issue_stubs[:ENTITY_SAMPLE_ISSUES]:
        try:
            issue = session.issue(stub.id)
        except RateLimitError as e:
            retry_after = retry_after_seconds(e)
            note_rate_limit(retry_after)
            current_app.logger.warning(
                "Metron rate limited after %d of %d sampled issues for series %s: %s",
                sampled, min(len(issue_stubs), ENTITY_SAMPLE_ISSUES), series_id, e)
            partial = True
            break
        except ApiError as e:
            current_app.logger.warning("Metron issue %s failed: %s", stub.id, e)
            continue

        sampled += 1
        if getattr(issue, "resource_url", None):
            issues[stub.id]["metron_url"] = str(issue.resource_url)

        for credit in getattr(issue, "credits", None) or []:
            if credit.creator and getattr(credit, "id", None):
                creators[credit.creator] = credit.id

        for char in getattr(issue, "characters", None) or []:
            char_name = getattr(char, "name", None)
            char_id = getattr(char, "id", None)
            if char_name and char_id:
                characters[char_name] = char_id

    return {
        "metron_id": series_id,
        "total_issues": len(issues),
        "sampled_issues": sampled,
        "partial": partial,
        "retry_after": retry_after,
        "total_creators": len(creators),
        "total_characters": len(characters),
        "issues": list(issues.values()),
        "creators": [{"metron_id": cid, "value": name} for name, cid in creators.items()],
        "characters": [{"metron_id": cid, "value": name} for name, cid in characters.items()],
    }
