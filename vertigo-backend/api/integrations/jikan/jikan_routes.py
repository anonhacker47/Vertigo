
from flask import Blueprint
from apifairy import authenticate, arguments
from marshmallow import Schema, fields
from api.utils.auth import token_auth
from api.integrations.jikan.client import get_jikan_session

jikan = Blueprint('jikan', __name__, url_prefix="/api")

class MangaSearchSchema(Schema):
    query = fields.Str(required=True)

@jikan.route("/jikan/manga/search", methods=["GET"])
@arguments(MangaSearchSchema, location="query")
@authenticate(token_auth)
def search_manga(args):
    session = get_jikan_session()
    query = args["query"]

    results = session.search_manga(query) or []
    items = []

    for m in results:
        items.append({
            "mal_id": m.get("mal_id"),
            "name": m.get("title"),
            "year_began": (m.get("published") or {}).get("from", "")[:4] or None,
            "chapter_count": m.get("chapters"),
            "volume_count": m.get("volumes"),
            "image_url": (m.get("images") or {}).get("webp", {}).get("large_image_url"),
        })

    return {
        "items": items,
        "total_found": len(items)
    }


@jikan.route("/jikan/manga/<int:manga_id>", methods=["GET"])
@authenticate(token_auth)
def manga_detail(manga_id):
    session = get_jikan_session()

    m = session.manga(manga_id)

    return {
        "mal_id": m.get("mal_id"),
        "name": m.get("title"),
        "year_began": (m.get("published") or {}).get("from", "")[:4] or None,
        "chapter_count": m.get("chapters"),
        "volume_count": m.get("volumes"),
        "status": m.get("status"),
        "publisher": {
            "mal_id": (m.get("publishers") or [{}])[0].get("mal_id"),
            "value": (m.get("publishers") or [{}])[0].get("name"),
        } if m.get("publishers") else None,
        "desc": m.get("synopsis"),
        "genres": [
            {"mal_id": g.get("mal_id"), "value": g.get("name")}
            for g in m.get("genres", [])
        ],
        "mal_url": m.get("url"),
        "image_url": (m.get("images") or {}).get("jpg", {}).get("large_image_url"),
    }




@jikan.route("/jikan/manga/<int:manga_id>/entities", methods=["GET"])
@authenticate(token_auth)
def manga_entities(manga_id):
    session = get_jikan_session()

    chars = session.manga_characters(manga_id) or []

    characters = []
    creators = []

    for c in chars:
        char = c.get("character") or {}
        characters.append({
            "mal_id": char.get("mal_id"),
            "value": char.get("name"),
        })

    m = session.manga(manga_id)
    for a in m.get("authors", []):
        creators.append({
            "mal_id": a.get("mal_id"),
            "value": a.get("name"),
        })

    return {
        "mal_id": manga_id,
        "total_creators": len(creators),
        "total_characters": len(characters),
        "creators": creators,
        "characters": characters,
    }
