from functools import wraps

from flask import Blueprint, current_app
from apifairy import authenticate, arguments
from marshmallow import Schema, fields
import requests

from api.utils.auth import token_auth
from api.integrations.tenrai.client import get_tenrai_session

tenrai = Blueprint('tenrai', __name__, url_prefix="/api")


class MangaSearchSchema(Schema):
    query = fields.Str(required=True)


def _upstream_message(resp):
    """Tenrai errors use a JSON envelope: {status, type, message, error, path}."""
    try:
        return (resp.json() or {}).get("message")
    except ValueError:
        return None


def handle_tenrai_errors(f):
    """Translate upstream Tenrai failures into clean API error responses."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except requests.exceptions.HTTPError as e:
            resp = e.response
            status = resp.status_code if resp is not None else None

            if status == 429:
                retry_after = (resp.headers or {}).get("Retry-After")
                current_app.logger.warning("Tenrai rate limited: %s", e)
                return {
                    "error": "rate_limited",
                    "retry_after": int(retry_after) if retry_after and retry_after.isdigit() else None,
                }, 429

            if status == 404:
                return {
                    "error": "not_found",
                    "message": _upstream_message(resp) or "Not found on MyAnimeList.",
                }, 404

            if status == 403:
                current_app.logger.error("Tenrai blocked this server (403): %s", e)
                return {
                    "error": "tenrai_error",
                    "message": "MyAnimeList (Tenrai) is refusing requests from this server. "
                               "This usually clears within 24 hours.",
                    "upstream_status": status,
                }, 502

            current_app.logger.warning("Tenrai request failed: %s", e)
            return {
                "error": "tenrai_error",
                "message": f"MyAnimeList (Tenrai) returned an error ({status}).",
                "upstream_status": status,
            }, 502

        except requests.exceptions.RequestException as e:
            current_app.logger.warning("Tenrai unreachable: %s", e)
            return {
                "error": "tenrai_unavailable",
                "message": "MyAnimeList (Tenrai) did not respond. Please try again shortly.",
            }, 504

    return wrapper


def _year_began(m):
    # Tenrai returns null for unknown dates, so guard before slicing.
    started = (m.get("published") or {}).get("from") or ""
    return started[:4] or None


def _image(m, fmt):
    return ((m.get("images") or {}).get(fmt) or {}).get("large_image_url")


def _ref(item):
    return {"mal_id": item.get("mal_id"), "value": item.get("name")}


@tenrai.route("/tenrai/manga/search", methods=["GET"])
@arguments(MangaSearchSchema, location="query")
@authenticate(token_auth)
@handle_tenrai_errors
def search_manga(args):
    session = get_tenrai_session()
    results = session.search_manga(args["query"]) or []

    items = [{
        "mal_id": m.get("mal_id"),
        "name": m.get("title"),
        "year_began": _year_began(m),
        "chapter_count": m.get("chapters"),
        "volume_count": m.get("volumes"),
        "image_url": _image(m, "webp"),
    } for m in results]

    return {
        "items": items,
        "total_found": len(items)
    }


@tenrai.route("/tenrai/manga/<int:manga_id>", methods=["GET"])
@authenticate(token_auth)
@handle_tenrai_errors
def manga_detail(manga_id):
    session = get_tenrai_session()

    m = session.manga(manga_id)
    if not m:
        return {"error": "not_found", "message": f"Manga {manga_id} not found."}, 404

    # MAL has no publisher on manga; the serialization magazine is the closest match.
    serializations = m.get("serializations") or []

    return {
        "mal_id": m.get("mal_id"),
        "name": m.get("title"),
        "year_began": _year_began(m),
        "chapter_count": m.get("chapters"),
        "volume_count": m.get("volumes"),
        "status": m.get("status"),
        "publisher": _ref(serializations[0]) if serializations else None,
        "desc": m.get("synopsis"),
        "genres": [_ref(g) for g in m.get("genres") or []],
        "mal_url": m.get("url"),
        "image_url": _image(m, "jpg"),
    }


@tenrai.route("/tenrai/manga/<int:manga_id>/entities", methods=["GET"])
@authenticate(token_auth)
@handle_tenrai_errors
def manga_entities(manga_id):
    session = get_tenrai_session()

    characters = [
        _ref(c.get("character") or {})
        for c in session.manga_characters(manga_id) or []
    ]

    m = session.manga(manga_id) or {}
    creators = [_ref(a) for a in m.get("authors") or []]

    return {
        "mal_id": manga_id,
        "total_creators": len(creators),
        "total_characters": len(characters),
        "creators": creators,
        "characters": characters,
    }
