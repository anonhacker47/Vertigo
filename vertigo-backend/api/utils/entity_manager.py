from api.app import db
from flask import current_app, json
from flask import current_app
from api.background import executor
from api.models.series_entities import Publisher, Creator, Character, Genre
from api import db
from api.integrations.mokkari.utils import fetch_metron_entity_info
from api.helpers.thumbnail_processing import get_or_download_thumbnail

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
    
def enrich_entity(app,entity_id, model_name, metron_type, metron_id, name, user_id):
    model = ENTITY_MODEL_MAP.get(model_name)
    folder = FOLDER_MAP.get(metron_type)

    if not model or not folder:
        return

    with app.app_context():
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
            db.session.remove()

def make_entity_cache_key(model, user, title):
    return f"{model.__tablename__}:{user.id}:{title.lower()}"

def create_or_get_entity(model, name, user, metron_type=None, metron_id=None):
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

    if hasattr(model, "metron_id"):
        kwargs["metron_id"] = metron_id

    entity = model(**kwargs)
    db.session.add(entity)
    db.session.commit()

    if metron_type and hasattr(model, "metron_id"):
        executor.submit(
            enrich_entity,
            current_app._get_current_object(),
            entity.id,
            model.__name__.lower(),
            metron_type,
            entity.metron_id,
            name,
            user.id
        )

    return entity