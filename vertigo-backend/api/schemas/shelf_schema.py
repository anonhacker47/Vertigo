from marshmallow import validate
from api import ma

SHELF_ORDERS = ("publisher", "series", "newest", "unread")
SHELF_SHOWS = ("all", "unread")
MAX_STANDEES = 2
SHELF_DEFAULTS = {"standees": None, "order": "publisher", "show": "unread", "publisher": None}


class ShelfSettingsSchema(ma.Schema):
    """How the 3D shelf is arranged. Null standees or publisher mean automatic, or any."""
    standees = ma.List(ma.Integer(), allow_none=True, load_default=None,
                           validate=validate.Length(max=MAX_STANDEES))
    order = ma.String(load_default="publisher", validate=validate.OneOf(SHELF_ORDERS))
    show = ma.String(load_default="unread", validate=validate.OneOf(SHELF_SHOWS))
    publisher = ma.Integer(allow_none=True, load_default=None)


def shelf_settings(user) -> dict:
    return {**SHELF_DEFAULTS, **(user.shelf_settings or {})}
