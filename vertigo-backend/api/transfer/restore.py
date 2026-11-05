"""Validate a backup zip and put it back into an account: fill an empty one, merge into a full one, or replace it."""
import io
import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone

from marshmallow import EXCLUDE, ValidationError
from sqlalchemy import func, select
from werkzeug.datastructures import FileStorage

from api import db, media
from api.helpers.cover_bg_generator import submit_background_regeneration
from api.models.issue import Issue
from api.models.series import Series
from api.models.user import User
from api.schemas.shelf_schema import ShelfSettingsSchema
from api.transfer import backup
from api.transfer.backup import (
    BACKUP_FORMAT, BACKUP_JSON, BACKUP_VERSION, ENTITY_COLUMNS, ENTITY_KEYS, ENTITY_MODELS,
    IMAGES_DIR, ISSUE_COLUMNS, SERIES_COLUMNS,
)
from api.transfer.errors import RestoreError
from api.utils.collection import delete_collection

MODES = ('merge', 'replace')


# --- reading --------------------------------------------------------------------------------

def stage(upload: FileStorage):
    """Save the upload and validate it; returns ``(path, info)`` or raises ``RestoreError``."""
    fd, path = tempfile.mkstemp(prefix='vertigo-restore-', suffix='.zip')
    try:
        with os.fdopen(fd, 'wb') as fh:
            upload.save(fh)
        data = load(path)
        plan(data)
        return path, describe(data)
    except Exception:
        discard(path)
        raise


def discard(path) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


def load(path) -> dict:
    """The validated ``backup.json`` of the zip at ``path``."""
    if not zipfile.is_zipfile(path):
        raise RestoreError('That file is not a Vertigo backup (.zip).')
    with zipfile.ZipFile(path) as zf:
        if BACKUP_JSON not in zf.namelist():
            raise RestoreError('The zip has no backup.json, so it is not a Vertigo backup.')
        try:
            data = json.loads(zf.read(BACKUP_JSON))
        except ValueError as exc:
            raise RestoreError('backup.json is not valid JSON.') from exc
    if not isinstance(data, dict) or data.get('format') != BACKUP_FORMAT:
        raise RestoreError('That file is not a Vertigo backup.')
    version = data.get('version')
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise RestoreError('The backup has no usable version number.')
    if version > BACKUP_VERSION:
        raise RestoreError(f'This backup was made by a newer Vertigo (format {version}); '
                           'update the server before restoring it.')
    for key in ('series', *ENTITY_KEYS.values()):
        if not isinstance(data.get(key, []), list):
            raise RestoreError(f'"{key}" in backup.json should be a list.')
    return data


def describe(data) -> dict:
    series = data.get('series') or []
    return {
        'version': data.get('version'),
        'created_at': data.get('created_at'),
        'username': (data.get('user') or {}).get('username'),
        'series': len(series),
        'issues': sum(len(s.get('issues') or []) for s in series),
        'entities': sum(len(data.get(k) or []) for k in ENTITY_KEYS.values()),
    }


def has_collection(user) -> bool:
    if db.session.scalar(user.series_select().limit(1)) is not None:
        return True
    return any(
        db.session.scalar(select(model.id).where(model.user_id == user.id).limit(1)) is not None
        for model in ENTITY_MODELS.values())


def account_counts(user) -> dict:
    count = lambda model: db.session.scalar(  # noqa: E731
        select(func.count()).select_from(model).where(model.user_id == user.id))
    return {
        'series': count(Series),
        'issues': count(Issue),
        'entities': sum(count(model) for model in ENTITY_MODELS.values()),
    }


# --- planning -------------------------------------------------------------------------------

def _coerce(value, column, label):
    """``value`` as the Python type of ``column``; dates come as ISO strings."""
    if value is None:
        return None
    kind = column.type.python_type
    try:
        if kind is datetime:
            if isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError
            dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
            return dt.astimezone(timezone.utc).replace(tzinfo=None) if dt.tzinfo else dt
        if kind is bool:
            return bool(value)
        if kind is int:
            if isinstance(value, float) and not value.is_integer():
                raise ValueError
            return int(value)
        if kind is float:
            return float(value)
        return str(value)
    except (TypeError, ValueError):
        raise RestoreError(f'{label}: "{value}" is not a valid {column.name}.') from None


def _columns(row, columns, model, label) -> dict:
    table = model.__table__.columns
    kwargs = {}
    for name in columns:
        if name in row and name in table:
            kwargs[name] = _coerce(row[name], table[name], label)
    return kwargs


def _title(row, label) -> str:
    title = str(row.get('title') or '').strip() if isinstance(row, dict) else ''
    if not title:
        raise RestoreError(f'{label} has no title.')
    return title


def plan(data) -> dict:
    """Everything in ``data`` as keyword arguments for the models, checked but not yet stored."""
    entities = {}
    for kind, key in ENTITY_KEYS.items():
        model = ENTITY_MODELS[kind]
        rows = []
        for index, row in enumerate(data.get(key) or []):
            label = f'{key}[{index}]'
            _title(row, label)
            rows.append((row.get('id'), _columns(row, ENTITY_COLUMNS, model, label), row.get('thumbnail')))
        entities[kind] = rows

    series = []
    for index, row in enumerate(data.get('series') or []):
        label = f'series[{index}]'
        title = _title(row, label)
        kwargs = _columns(row, SERIES_COLUMNS, Series, label)
        links = {}
        for kind in ENTITY_MODELS:
            ids = row.get(f'{kind}_ids') or []
            if not isinstance(ids, list):
                raise RestoreError(f'"{title}": {kind}_ids should be a list.')
            links[kind] = ids
        issues, seen = [], set()
        for j, irow in enumerate(row.get('issues') or []):
            ilabel = f'"{title}" issue {j}'
            if not isinstance(irow, dict):
                raise RestoreError(f'{ilabel} is not an object.')
            number = irow.get('number')
            if isinstance(number, bool) or not isinstance(number, int) or number < 0:
                raise RestoreError(f'{ilabel}: the number is missing or not a whole number.')
            if number in seen:
                continue
            seen.add(number)
            ikwargs = _columns(irow, ISSUE_COLUMNS, Issue, ilabel)
            ikwargs['title'] = (ikwargs.get('title') or '').strip() or str(number)
            ikwargs['is_owned'] = int(bool(ikwargs.get('is_owned')))
            ikwargs['is_read'] = int(bool(ikwargs.get('is_read')))
            issues.append((ikwargs, irow.get('thumbnail')))
        series.append({'kwargs': kwargs, 'thumbnail': row.get('thumbnail'), 'links': links, 'issues': issues})
    shelf = (data.get('user') or {}).get('shelf_settings')
    if shelf is not None:
        try:
            shelf = ShelfSettingsSchema(unknown=EXCLUDE).load(shelf)
        except ValidationError:
            raise RestoreError('user.shelf_settings is not valid.') from None
    return {'entities': entities, 'series': series, 'shelf': shelf}


# --- applying -------------------------------------------------------------------------------

def _find_entity(model, user, kwargs):
    own = select(model).where(model.user_id == user.id)
    for key in ('metron_id', 'mal_id'):
        value = kwargs.get(key)
        if value not in (None, '') and hasattr(model, key):
            found = db.session.scalar(own.where(getattr(model, key) == value).limit(1))
            if found is not None:
                return found
    return db.session.scalar(own.where(model.title == kwargs['title']).limit(1))


def _find_series(user, kwargs):
    """Match by Metron id, else by title among series without one, so same-titled series with other ids stay apart."""
    own = user.series_select()
    same_title = func.lower(Series.title) == kwargs['title'].casefold()
    metron_id = kwargs.get('metron_id')
    if metron_id not in (None, ''):
        found = db.session.scalar(own.where(Series.metron_id == str(metron_id)).limit(1))
        if found is not None:
            return found
        unlinked = (Series.metron_id.is_(None)) | (Series.metron_id == '')
        return db.session.scalar(own.where(same_title, unlinked).limit(1))
    return db.session.scalar(own.where(same_title).limit(1))


def _restore_image(zf, members, relpath, user_id, rel_dir, filename, target, attr='thumbnail') -> bool:
    """Store the backup's image for ``relpath`` under the new record's path; False when absent."""
    member = f'{IMAGES_DIR}/{relpath}' if relpath else None
    if member not in members or zf.getinfo(member).file_size > media.MAX_IMAGE_BYTES:
        return False
    try:
        source = FileStorage(io.BytesIO(zf.read(member)), filename=os.path.basename(member))
        stored, _ = media.store(user_id, rel_dir, filename, source)
    except (media.MediaError, zipfile.BadZipFile, KeyError):
        return False
    setattr(target, attr, stored)
    return True


def _remap_shelf(shelf, entity_map) -> dict:
    """The backed-up shelf arrangement pointed at the restored character and publisher rows."""
    characters, publishers = entity_map['character'], entity_map['publisher']
    standees = [characters[i].id for i in shelf['standees'] or [] if i in characters]
    publisher = publishers.get(shelf['publisher'])
    return {**shelf, 'standees': standees or None, 'publisher': publisher.id if publisher else None}


def apply(run, path, user_id, mode) -> dict:
    """Worker entry; takes the user id because it runs in another thread with its own session."""
    user = db.session.get(User, user_id)
    if user is None:
        raise RestoreError('The account no longer exists.')
    data = load(path)
    work = plan(data)
    summary = {'series': 0, 'series_matched': 0, 'issues': 0, 'issues_skipped': 0,
               'entities': 0, 'entities_matched': 0, 'images': 0}
    run.summary = summary

    was_empty = not has_collection(user)
    if mode == 'replace' and not was_empty:
        summary['safety_backup'] = backup.save_safety_copy(user)
        delete_collection(user)
        db.session.commit()
        was_empty = True
    merge = not was_empty
    covers = False

    with zipfile.ZipFile(path) as zf:
        members = set(zf.namelist())

        entity_map = {kind: {} for kind in ENTITY_MODELS}
        for kind, rows in work['entities'].items():
            model = ENTITY_MODELS[kind]
            for old_id, kwargs, thumbnail in rows:
                entity = _find_entity(model, user, kwargs) if merge else None
                if entity is None:
                    entity = model(user=user, **kwargs)
                    db.session.add(entity)
                    db.session.flush()
                    summary['entities'] += 1
                    if kind in media.ENTITY_KINDS and _restore_image(
                            zf, members, thumbnail, user.id, media.entity_dir(kind), str(entity.id), entity):
                        summary['images'] += 1
                else:
                    summary['entities_matched'] += 1
                if old_id is not None:
                    entity_map[kind][old_id] = entity
                run.done += 1
            db.session.commit()

        for item in work['series']:
            kwargs, links, issues = item['kwargs'], item['links'], item['issues']
            series = _find_series(user, kwargs) if merge else None
            if series is None:
                series = Series(user=user, **kwargs)
                db.session.add(series)
                for kind, old_ids in links.items():
                    chosen = [entity_map[kind][i] for i in old_ids if i in entity_map[kind]]
                    setattr(series, kind, chosen)
                db.session.flush()
                if _restore_image(zf, members, item['thumbnail'], user.id,
                                  media.series_dir(series.id), 'cover', series):
                    summary['images'] += 1
                    covers = True
                summary['series'] += 1
                have = set()
            else:
                summary['series_matched'] += 1
                have = {i.number for i in db.session.scalars(series.issue_select())}
            run.done += 1

            for ikwargs, thumbnail in issues:
                if ikwargs['number'] in have:
                    summary['issues_skipped'] += 1
                    run.done += 1
                    continue
                issue = Issue(user=user, series=series, **ikwargs)
                db.session.add(issue)
                db.session.flush()
                if _restore_image(zf, members, thumbnail, user.id,
                                  media.issues_dir(series.id), str(issue.id), issue):
                    summary['images'] += 1
                have.add(ikwargs['number'])
                summary['issues'] += 1
                run.done += 1
            series.refresh_counts()
            db.session.commit()

        backup_user = data.get('user') or {}
        currency = backup_user.get('preferred_currency')
        if was_empty and isinstance(currency, str) and len(currency) == 3:
            user.preferred_currency = currency.upper()
        if user.shelf_settings is None and work['shelf'] is not None:
            user.shelf_settings = _remap_shelf(work['shelf'], entity_map)
        if not user.profile_picture and _restore_image(
                zf, members, backup_user.get('profile_picture'), user.id,
                media.AVATAR_DIR, 'avatar', user, attr='profile_picture'):
            summary['images'] += 1
        db.session.commit()

    if covers:
        submit_background_regeneration(user.id)
    return summary
