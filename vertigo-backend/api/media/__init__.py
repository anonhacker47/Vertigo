"""
Storage for user-uploaded images (series covers, issue covers, entity thumbnails, avatars).

On-disk layout, relative to DATA_DIR (default ``<backend>/Config``, override with the
``VERTIGO_DATA_DIR`` environment variable)::

    users/<user_id>/
        avatar/avatar.<ext>
        series/<series_id>/cover.<ext>
        series/<series_id>/issues/<issue_id>.<ext>
        entities/<kind>/<entity_id>.<ext>        kind = publisher | creator | character

Model columns (``thumbnail`` / ``profile_picture``) store the path *relative to the
user's root*, e.g. ``series/12/cover.jpeg``. Installs created before this layout are
moved into it by ``api.media_migrate`` (run at startup and via ``flask media migrate``).

Routes never build paths themselves: they call ``apply_thumbnail_field`` / ``store`` /
``remove`` / ``send`` and persist the returned relative path.

Modules:

    paths           on-disk layout constants and path resolution
    storage         fetch, validate and persist image bytes
    web             the request/response contract shared by every image route
    dominant_color  accent colour extraction for covers
    task_queue      background workers for slow image jobs
"""
from api.media.paths import (
    USERS_DIR, AVATAR_DIR, SERIES_DIR, ISSUES_DIR, ENTITIES_DIR, ENTITY_KINDS,
    data_dir, user_root, series_dir, issues_dir, entity_dir, init_user_dirs, resolve,
)
from api.media.storage import (
    MediaError, MAX_IMAGE_BYTES, store, remove, remove_dir, delete_user_media,
)
from api.media.web import NOIMAGE, send, apply_thumbnail_field
from api.media.dominant_color import dominant_color
from api.media.task_queue import start_media_worker, submit

__all__ = [
    # paths
    "USERS_DIR", "AVATAR_DIR", "SERIES_DIR", "ISSUES_DIR", "ENTITIES_DIR", "ENTITY_KINDS",
    "data_dir", "user_root", "series_dir", "issues_dir", "entity_dir", "init_user_dirs",
    "resolve",
    # storage
    "MediaError", "MAX_IMAGE_BYTES", "store", "remove", "remove_dir", "delete_user_media",
    # web
    "NOIMAGE", "send", "apply_thumbnail_field",
    # dominant_color
    "dominant_color",
    # task_queue
    "start_media_worker", "submit",
]
