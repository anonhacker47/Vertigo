from api.app import db
from flask import json
from api.models.series_entities import Publisher, Creator, Character, Genre
from api import db
from api.integrations.mokkari.utils import fetch_metron_entity_info
from api import media
from api.integrations.mokkari.task_queue import submit_mokkari_task
from api.integrations.tenrai.utils import fetch_tenrai_entity_info
from api.integrations.tenrai.task_queue import submit_tenrai_task

ENTITY_MODEL_MAP = {
    "publisher": Publisher,
    "genre": Genre,
    "creator": Creator,
    "character": Character,
}

def _store_entity_thumbnail(entity, kind, url, user_id):
    """Download ``url`` as the entity's thumbnail; returns the new relpath or None."""
    try:
        relpath, _ = media.store(
            user_id, media.entity_dir(kind), str(entity.id), url,
            replace=entity.thumbnail,
        )
        return relpath
    except media.MediaError:
        return None

def safe_json_list(val):
    try:
        data = json.loads(val) if val else []
        return data if isinstance(data, list) else []
    except Exception:
        return []
    
def enrich_entity(entity_id, model_name, metron_type, metron_id, name, user_id):
    model = ENTITY_MODEL_MAP.get(model_name)

    if not model or metron_type not in media.ENTITY_KINDS:
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
            thumb = _store_entity_thumbnail(entity, metron_type, str(info.image), user_id)
            if thumb:
                entity.thumbnail = thumb
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
            db.session.close()

def enrich_tenrai_entity(entity_id, model_name, entity_type, mal_id, name, user_id):
    model = ENTITY_MODEL_MAP.get(model_name)

    if not model or entity_type not in media.ENTITY_KINDS:
        return

    try:
        entity = db.session.get(model, entity_id)
        if not entity:
            return
        info = fetch_tenrai_entity_info(entity_type, mal_id)
        if not info:
            return
        if hasattr(entity, "description") and info.get("about"):
            entity.description = info.get("about")

        image_url = ((info.get("images") or {}).get("jpg") or {}).get("image_url")
        if image_url:
            thumb = _store_entity_thumbnail(entity, entity_type, image_url, user_id)
            if thumb:
                entity.thumbnail = thumb
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
            db.session.close()


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
        submit_tenrai_task(
            enrich_tenrai_entity,
            entity.id,
            model.__name__.lower(),
            entity_type,
            entity.mal_id,
            name,
            user.id
        )

    return entity