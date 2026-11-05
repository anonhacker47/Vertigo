"""Removing everything a user has catalogued while keeping the account."""
import sqlalchemy as sqla
from sqlalchemy.orm import selectinload

from api import db, media
from api.models.series import Series
from api.models.series_entities import Character, Creator, Genre, Publisher

ENTITY_MODELS = (Publisher, Character, Creator, Genre)


def delete_collection(user) -> dict:
    """Delete the user's series, issues, entities and images; the caller commits."""
    deleted = {}
    series_list = db.session.scalars(user.series_select().options(selectinload(Series.issue))).all()
    for series in series_list:
        db.session.delete(series)
    deleted['series'] = len(series_list)

    for model in ENTITY_MODELS:
        items = db.session.scalars(sqla.select(model).filter_by(user_id=user.id)).all()
        for item in items:
            db.session.delete(item)
        deleted[model.__tablename__] = len(items)

    media.delete_user_media(user.id, keep_avatar=True)
    user.shelf_settings = None  # its standees and publisher are gone
    return deleted
