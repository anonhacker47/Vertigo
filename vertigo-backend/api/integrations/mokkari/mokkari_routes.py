from flask import Blueprint, current_app
from apifairy import authenticate, other_responses, arguments
from marshmallow import Schema, fields
from mokkari.exceptions import RateLimitError, ApiError

from api.integrations.mokkari.mokkari_rate_limiter import wait_for_mokkari_slot
from api.integrations.mokkari.client import get_mokkari_session
from api.utils.auth import token_auth

mokkari = Blueprint('mokkari', __name__, url_prefix="/api")

class SearchQuerySchema(Schema):
    query = fields.Str(required=True)

@mokkari.route("/metron_search", methods=["GET"])
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
        return {"error": "rate_limited", "retry_after": e.retry_after}, 429
    except ApiError as e:
        return {"error": "metron_error", "message": str(e)}, 502

class SeriesIdSchema(Schema):
    series_id = fields.Int(required=True)

@mokkari.route("/series_detail", methods=["GET"])
@arguments(SeriesIdSchema, location="query")
@authenticate(token_auth)
def get_series_detail(args):
    series_id = args["series_id"]
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
        return {"error": "rate_limited", "retry_after": e.retry_after}, 429
    except ApiError as e:
        return {"error": "metron_error", "message": str(e)}, 502
    
class SeriesCreatorsSchema(Schema):
    series_id = fields.Int(required=True)

@mokkari.route("/series_entities", methods=["GET"])
@arguments(SeriesCreatorsSchema, location="query")
@authenticate(token_auth)
def get_series_entities(args):
    series_id = args["series_id"]
    session = get_mokkari_session()

    if not session:
        return {"error": "no_session"}, 500

    try:
        wait_for_mokkari_slot()
        issue_stubs = session.issues_list({"series_id": series_id})

        creators = {}    
        characters = {}  
        issue_count = 0

        for stub in issue_stubs:
            issue_count += 1
            issue = session.issue(stub.id)

            if issue.credits:
                for credit in issue.credits:
                    if credit.creator and getattr(credit, "id", None):
                        creators[credit.creator] = credit.id

            if issue.characters:
                for char in issue.characters:
                    char_name = getattr(char, "name", None)
                    char_id = getattr(char, "id", None)
                    if char_name and char_id:
                        characters[char_name] = char_id
        return {
            "metron_id": series_id,
            "total_issues": issue_count,
            "total_creators": len(creators),
            "total_characters": len(characters),
            "creators": [{"metron_id": cid, "value": name} for name, cid in creators.items()],
            "characters": [{"metron_id": cid, "value": name} for name, cid in characters.items()],
        }

    except RateLimitError as e:
        return {"error": "rate_limited", "retry_after": e.retry_after}, 429
    except ApiError as e:
        return {"error": "metron_error", "message": str(e)}, 502