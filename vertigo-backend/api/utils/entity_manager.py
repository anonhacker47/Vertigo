from api.app import db
from flask import json
from api.models.series_entities import Publisher, Creator, Character, Genre
from api import db
from api.integrations.mokkari.utils import fetch_metron_entity_info
from api.helpers.thumbnail_processing import get_or_download_thumbnail
from api.integrations.mokkari.task_queue import submit_mokkari_task
from api.integrations.jikan.utils import fetch_jikan_entity_info
from api.integrations.jikan.task_queue import submit_jikan_task

ENTITY_MODEL_MAP = {
    "publisher": Publisher,
    "genre": Genre,
    "creator": Creator,
    "character": Character,
}

FOLDER_MAP = {
    "character": "Entities/Character",
    "creator": "Entities/Creator",
    "publisher": "Entities/Publisher",
}

def safe_json_list(val):
    try:
        data = json.loads(val) if val else []
        return data if isinstance(data, list) else []
    except Exception:
        return []
    
def enrich_entity(entity_id, model_name, metron_type, metron_id, name, user_id):
    model = ENTITY_MODEL_MAP.get(model_name)
    folder = FOLDER_MAP.get(metron_type)

    if not model or not folder:
        return

    try:
        entity = db.session.get(model, entity_id)
        if not entity:
            return
        info = fetch_metron_entity_info(metron_type, metron_id)
        if not info:
            return
        if hasattr(entity, "description"):
            entity.description = getattr(info, "desc", None)
        if getattr(info, "image", None):
            thumb, _ = get_or_download_thumbnail(
                str(info.image),
                name,
                user_id,
                folder
            )
            if thumb:
                entity.thumbnail = thumb
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
            db.session.close()

def enrich_jikan_entity(entity_id, model_name, jikan_type, mal_id, name, user_id):
    model = ENTITY_MODEL_MAP.get(model_name)
    folder = FOLDER_MAP.get(jikan_type)

    if not model or not folder:
        return

    try:
        entity = db.session.get(model, entity_id)
        if not entity:
            return
        info = fetch_jikan_entity_info(jikan_type, mal_id)
        if not info:
            return
        if hasattr(entity, "description") and info.get("about"):
            entity.description = info.get("about")
            
        image_url = info.get("images", {}).get("jpg", {}).get("image_url")
        if image_url:
            thumb, _ = get_or_download_thumbnail(
                image_url,
                name,
                user_id,
                folder
            )
            if thumb:
                entity.thumbnail = thumb
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
            db.session.close()


def make_entity_cache_key(model, user, title):
    return f"{model.__tablename__}:{user.id}:{title.lower()}"

def create_or_get_entity(model, name, user, entity_type=None, external_id=None, series_is_manga=False):
    if not name:
        return None

    name = name.strip()

    entity = (
        db.session.query(model)
        .filter_by(title=name, user=user)
        .first()
    )
    if entity:
        return entity

    kwargs = {
        "title": name,
        "user": user,
    }

    if not series_is_manga and hasattr(model, "metron_id"):
        kwargs["metron_id"] = external_id
    elif series_is_manga and hasattr(model, "mal_id"):
        kwargs["mal_id"] = external_id

    entity = model(**kwargs)
    db.session.add(entity)
    db.session.commit()

    if (
        not series_is_manga
        and entity_type
        and hasattr(model, "metron_id")
        and entity.metron_id
    ):
        submit_mokkari_task(
            enrich_entity,
            entity.id,
            model.__name__.lower(),
            entity_type,
            entity.metron_id,
            name,
            user.id
        )
    elif (
        series_is_manga
        and entity_type
        and hasattr(model, "mal_id")
        and entity.mal_id
    ):
        submit_jikan_task(
            enrich_jikan_entity,
            entity.id,
            model.__name__.lower(),
            entity_type,
            entity.mal_id,
            name,
            user.id
        )

    return entity