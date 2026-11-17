from flask import abort

from api import db
from api.utils.auth import token_auth


def owned_or_403(model, id):
    """The row with this id when it belongs to the caller; 404 when missing, 403 when someone else's."""
    row = db.session.get(model, id) or abort(404)
    if row.user_id != token_auth.current_user().id:
        abort(403)
    return row
