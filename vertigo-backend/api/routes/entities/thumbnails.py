"""Shared multipart thumbnail handling for publisher / creator / character routes."""
from flask import jsonify, request

from api import media


def apply_entity_thumbnail(entity, kind: str, user_id):
    """Apply the request's ``thumbnail`` field (file, URL, "noimage") to ``entity``.

    Returns an error response tuple to send back, or None on success. The entity must
    already have an id (flush first on create) because files are stored by id.
    """
    try:
        state, relpath, _ = media.apply_thumbnail_field(
            user_id, request.form, request.files, 'thumbnail',
            rel_dir=media.entity_dir(kind), filename=str(entity.id),
            current=entity.thumbnail,
        )
    except media.MediaError as exc:
        return jsonify({"error": f"Failed to save thumbnail: {exc}"}), 400

    if state == 'set':
        entity.thumbnail = relpath
    elif state == 'cleared':
        entity.thumbnail = None
    return None
