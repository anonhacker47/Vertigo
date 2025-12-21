from flask import Blueprint
from apifairy import authenticate, other_responses, arguments
from marshmallow import Schema, fields
from mokkari.exceptions import RateLimitError, ApiError

from api.integrations.mokkari.client import get_mokkari_session
from api.utils.auth import token_auth

search_metron = Blueprint('search_metron', __name__, url_prefix="/api")

class SearchQuerySchema(Schema):
    query = fields.Str(required=True)

@search_metron.route("/metron_search", methods=["GET"])
@arguments(SearchQuerySchema, location="query")
def search_series(args):
    query = args["query"]
    session = get_mokkari_session()

    series_list = session.series_list({"name": query})

    items = []
    try:
        for s in series_list[:5]:
            issues = session.issues_list({
                "series_id": s.id,
                "number": "1"
            })
    
            image = str(issues[0].image) if issues else None
    
            items.append({
                "series_id": s.id,
                "name": s.display_name,
                "year_began": s.year_began,
                "issue_count": s.issue_count,
                "volume": s.volume,
                "image": image,
            })
    
        return {
            "items": items,
            "total_found": len(series_list)
        }

    except RateLimitError as e:
        return {"error": "rate_limited", "retry_after": e.retry_after}, 429
    except ApiError as e:
        return {"error": "metron_error", "message": str(e)}, 502