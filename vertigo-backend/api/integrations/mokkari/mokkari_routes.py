from flask import Blueprint
from apifairy import authenticate, other_responses, arguments
from marshmallow import Schema, fields
from mokkari.exceptions import RateLimitError, ApiError

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
        series_list = session.series_list({"name": query})
        items = []

        for s in series_list:
            # 🔹 Fetch full series details
            # series = session.series(s.id)

            # 🔹 Fetch first issue for image
            # issues = session.issues_list({
            #     "series_id": s.id,
            #     "number": "1"
            # })
            # image = str(issues[0].image) if issues else None

            items.append({
                "series_id": s.id,
                "name": s.display_name,
                "year_began": s.year_began,
                # "year_end": series.year_end,
                "issue_count": s.issue_count,
                "volume": s.volume,
                # "series_type": series.series_type.name if series.series_type else None,
                # "publisher": series.publisher.name if series.publisher else None,
                # "genres": [g.name for g in (series.genres or [])],
                # "resource_url": str(series.resource_url),
                # "image": image,
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
# @authenticate(token_auth)
def get_series_detail(args):
    series_id = args["series_id"]
    session = get_mokkari_session()
    if not session:
        return {"error": "no_session"}, 500

    try:
        # Fetch the series details directly
        series = session.series(series_id)

        # Fetch first issue to get image
        issues = session.issues_list({"series_id": series_id, "number": "1"})
        first_issue_image = str(issues[0].image) if issues else None


        return {
            "series_id": series.id,
            "name": series.name,
            "volume": series.volume,
            "year_began": series.year_began,
            "year_end": getattr(series, "year_end", None),
            "issue_count": series.issue_count,
            "status": getattr(series, "status", None),
            "publisher": getattr(series.publisher, "name", None) if getattr(series, "publisher", None) else None,
            "imprint": getattr(series.imprint, "name", None) if getattr(series, "imprint", None) else None,
            "desc": getattr(series, "desc", None),
            "genres": [g.name for g in getattr(series, "genres", [])],
            "resource_url": str(getattr(series, "resource_url", None)) if getattr(series, "resource_url", None) else None,
            "image_first_issue": first_issue_image
        }

    except RateLimitError as e:
        return {"error": "rate_limited", "retry_after": e.retry_after}, 429
    except ApiError as e:
        return {"error": "metron_error", "message": str(e)}, 502
