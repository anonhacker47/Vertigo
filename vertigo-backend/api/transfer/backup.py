"""A user's collection as one zip: a versioned backup.json (ids kept so restore can follow links) plus every image."""
import io
import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone

from flask import current_app
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api import db, media
from api.models.series import Series
from api.models.series_entities import Character, Creator, Genre, Publisher

BACKUP_FORMAT = 'vertigo-backup'
BACKUP_VERSION = 1
BACKUP_JSON = 'backup.json'
IMAGES_DIR = 'images'

# Server-side copies taken before a destructive restore, under <DATA_DIR>/backups/.
SAFETY_DIR = 'backups'
SAFETY_KEEP = 3

ENTITY_MODELS = {'publisher': Publisher, 'creator': Creator, 'character': Character, 'genre': Genre}
ENTITY_KEYS = {'publisher': 'publishers', 'creator': 'creators', 'character': 'characters', 'genre': 'genres'}

# id and thumbnail are kept apart: both change on restore
SERIES_COLUMNS = ('title', 'description', 'notes', 'user_rating', 'manga', 'release_date',
                  'purchase_cost', 'series_format', 'issue_count', 'read_count', 'owned_count',
                  'dominant_color', 'slug', 'timestamp', 'metron_id', 'metron_url')
ISSUE_COLUMNS = ('title', 'number', 'description', 'cover_date', 'notes', 'slug', 'is_read',
                 'is_owned', 'bought_price', 'user_rating', 'bought_date', 'read_date',
                 'timestamp', 'metron_id', 'metron_url')
ENTITY_COLUMNS = ('title', 'description', 'slug', 'timestamp', 'metron_id', 'metron_url',
                  'mal_id', 'mal_url')
BOOL_COLUMNS = {'is_read', 'is_owned', 'manga'}


def _value(obj, column):
    value = getattr(obj, column, None)
    if isinstance(value, datetime):
        return value.isoformat()
    if column in BOOL_COLUMNS and value is not None:
        return bool(value)
    return value


def _record(obj, columns) -> dict:
    data = {'id': obj.id, 'thumbnail': getattr(obj, 'thumbnail', None)}
    data.update((c, _value(obj, c)) for c in columns if hasattr(obj, c))
    return data


def serialize(user) -> dict:
    """The ``backup.json`` document for ``user``."""
    data = {
        'format': BACKUP_FORMAT,
        'version': BACKUP_VERSION,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'app_version': current_app.config.get('SERVER_VERSION'),
        'user': {
            'username': user.username,
            'email': user.email,
            'preferred_currency': user.preferred_currency,
            'profile_picture': user.profile_picture,
            'shelf_settings': user.shelf_settings,
        },
    }
    for kind, model in ENTITY_MODELS.items():
        rows = db.session.scalars(select(model).where(model.user_id == user.id).order_by(model.id))
        data[ENTITY_KEYS[kind]] = [_record(e, ENTITY_COLUMNS) for e in rows]

    series_list = db.session.scalars(
        user.series_select().options(selectinload(Series.issue)).order_by(Series.id)).all()
    data['series'] = []
    for series in series_list:
        record = _record(series, SERIES_COLUMNS)
        for kind in ENTITY_MODELS:
            record[f'{kind}_ids'] = [e.id for e in getattr(series, kind)]
        record['issues'] = [_record(i, ISSUE_COLUMNS)
                            for i in sorted(series.issue, key=lambda i: (i.number, i.id))]
        data['series'].append(record)
    return data


def image_paths(user_id, data) -> list:
    """``(absolute path, zip member name)`` for every image the document refers to that exists."""
    relpaths = [(data.get('user') or {}).get('profile_picture')]
    for key in ENTITY_KEYS.values():
        relpaths += [row.get('thumbnail') for row in data.get(key, [])]
    for series in data.get('series', []):
        relpaths.append(series.get('thumbnail'))
        relpaths += [issue.get('thumbnail') for issue in series.get('issues', [])]
    found, seen = [], set()
    for relpath in relpaths:
        full = media.resolve(user_id, relpath) if relpath else None
        if full and relpath not in seen:
            seen.add(relpath)
            found.append((full, f'{IMAGES_DIR}/{relpath}'))
    return found


def write(user, fileobj) -> dict:
    """Write the backup zip for ``user`` to an open binary file; returns the document."""
    data = serialize(user)
    with zipfile.ZipFile(fileobj, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(BACKUP_JSON, json.dumps(data, ensure_ascii=False, indent=1))
        for full, member in image_paths(user.id, data):
            try:
                zf.write(full, member)
            except OSError:
                # An image replaced or removed while we were zipping is not worth losing the backup over.
                continue
    return data


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')


def build(user):
    """Write the zip to a temporary file; returns ``(open file at offset 0, download name)``."""
    tmp = tempfile.TemporaryFile(prefix='vertigo-backup-')
    write(user, tmp)
    tmp.seek(0)
    return tmp, f'vertigo-backup-{user.username}-{_stamp()[:-2]}.zip'


def save_safety_copy(user, reason: str = 'replace') -> str:
    """Zip the current collection into <DATA_DIR>/backups/ before it is destroyed; keeps the newest SAFETY_KEEP per user."""
    folder = os.path.join(media.data_dir(), SAFETY_DIR)
    os.makedirs(folder, exist_ok=True)
    prefix = f'before-{reason}-user{user.id}-'
    name = f'{prefix}{_stamp()}.zip'
    path = os.path.join(folder, name)
    partial = path + '.part'
    with open(partial, 'wb') as fh:
        write(user, fh)
    os.replace(partial, path)

    older = sorted(
        (f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith('.zip')),
        key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
    for stale in older[SAFETY_KEEP:]:
        try:
            os.remove(os.path.join(folder, stale))
        except OSError:
            pass
    return name
