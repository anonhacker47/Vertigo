from flask import jsonify, send_file

from api.media.paths import resolve
from api.media.storage import MediaError, store, remove

# Returned when no image is set; also accepted on upload to clear one.
NOIMAGE = "noimage"


def send(user_id, relpath):
    if not relpath:
        return jsonify(NOIMAGE)
    path = resolve(user_id, relpath)
    if not path:
        return jsonify("Image file not found"), 404
    return send_file(path)


def apply_thumbnail_field(user_id, form, files, field: str, *, rel_dir: str,
                          filename: str, current, want_color: bool = False):
    
    file = files.get(field) if files else None
    if file is not None and file.filename:
        relpath, color = store(user_id, rel_dir, filename, file, replace=current,
                               want_color=want_color)
        return "set", relpath, color

    if field not in form:
        return "unchanged", None, None

    value = (form.get(field) or "").strip()
    if value == (current or "") and value:
        return "unchanged", None, None
    if "/api/" in value:
        return "unchanged", None, None
    if value in ("", NOIMAGE):
        if current:
            remove(user_id, current)
        return "cleared", None, None
    if value.startswith(("http://", "https://")):
        relpath, color = store(user_id, rel_dir, filename, value, replace=current,
                               want_color=want_color)
        return "set", relpath, color

    raise MediaError("unsupported image source")
