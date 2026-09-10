"""
One-off migration from the legacy image layout to the one described in ``api.media``.

Legacy::

    Config/User/<uid>/Avatar/<uuid><slug>.ext
    Config/User/<uid>/Covers/<uuid><slug>.ext
    Config/User/<uid>/Entities/{Publisher,Creator,Character}/<uuid><slug>.ext

New::

    Config/users/<uid>/avatar/avatar.ext
    Config/users/<uid>/series/<sid>/cover.ext
    Config/users/<uid>/entities/<kind>/<id>.ext

Column values change from bare filenames to relative paths. Rows whose value already
contains ``/`` are skipped, so the command is safe to run repeatedly. Files that no row
references are reported and left in place.
"""
import os
import shutil

from api import db
from api import media
from api.models.user import User
from api.models.series_entities import Publisher, Creator, Character

_EXT_ALIASES = {".jpg": ".jpeg", ".jpe": ".jpeg"}

# The layout this script migrates away from: Config/User/<uid>/<Folder>/<uuid><slug>.ext,
# with bare filenames in the columns. Nothing outside this module knows about it.
LEGACY_USERS_DIR = "User"
LEGACY_DIRS = {
    "avatar": "Avatar",
    "series": "Covers",
    "publisher": "Entities/Publisher",
    "creator": "Entities/Creator",
    "character": "Entities/Character",
}


def legacy_user_root(user_id) -> str:
    return os.path.join(media.data_dir(), LEGACY_USERS_DIR, str(user_id))


def _ext(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return _EXT_ALIASES.get(ext, ext)


def _move(src: str, dest: str, dry_run: bool, log) -> None:
    log(f"  {os.path.relpath(src, media.data_dir())}  ->  {os.path.relpath(dest, media.data_dir())}")
    if dry_run:
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.move(src, dest)


def _prune_empty_dirs(root: str) -> None:
    if not os.path.isdir(root):
        return
    for dirpath, _dirnames, _filenames in os.walk(root, topdown=False):
        # Re-check at removal time: os.walk listed the children before they were pruned.
        if not os.listdir(dirpath):
            try:
                os.rmdir(dirpath)
            except OSError:
                pass


def migrate_media(dry_run: bool = False, purge_orphans: bool = False, log=print) -> dict:
    """Move legacy files and rewrite columns. Returns a summary dict.

    ``purge_orphans`` deletes legacy files that no database row references
    (leftovers from replaced covers and avatars); otherwise they are only reported.
    """
    summary = {"moved": 0, "missing": 0, "orphans": 0, "purged": 0, "users": 0}

    users = db.session.scalars(User.select()).all()
    for user in users:
        legacy_root = legacy_user_root(user.id)
        new_root = media.user_root(user.id)
        moved_sources: set[str] = set()
        summary["users"] += 1
        log(f"user {user.id} ({user.username})")

        def relocate(obj, column, legacy_dir, rel_dir, stem):
            value = getattr(obj, column)
            if not value or "/" in value:
                return
            src = os.path.join(legacy_root, legacy_dir, value)
            if not os.path.isfile(src):
                # Try the new root too: on case-insensitive filesystems User/ and users/
                # are the same directory and a previous partial run may have moved it.
                alt = os.path.join(new_root, legacy_dir, value)
                if os.path.isfile(alt):
                    src = alt
                else:
                    log(f"  missing file for {obj.__class__.__name__} {obj.id}: {value}")
                    summary["missing"] += 1
                    return
            new_rel = f"{rel_dir}/{stem}{_ext(src)}"
            _move(src, os.path.join(new_root, new_rel), dry_run, log)
            moved_sources.add(os.path.abspath(src))
            setattr(obj, column, new_rel)
            summary["moved"] += 1

        for s in db.session.scalars(user.series_select()).all():
            relocate(s, "thumbnail", LEGACY_DIRS["series"],
                     media.series_dir(s.id), "cover")

        for kind, model in (("publisher", Publisher), ("creator", Creator),
                            ("character", Character)):
            rows = db.session.scalars(
                model.select().where(model.user_id == user.id)
            ).all()
            for e in rows:
                relocate(e, "thumbnail", LEGACY_DIRS[kind],
                         media.entity_dir(kind), str(e.id))

        relocate(user, "profile_picture", LEGACY_DIRS["avatar"],
                 media.AVATAR_DIR, "avatar")

        if dry_run:
            db.session.rollback()
        else:
            db.session.commit()
            media.init_user_dirs(user.id)

        # Anything in the legacy folders that no row referenced is an orphan.
        for legacy_dir in LEGACY_DIRS.values():
            folder = os.path.join(legacy_root, legacy_dir)
            if not os.path.isdir(folder):
                continue
            for name in os.listdir(folder):
                path = os.path.join(folder, name)
                if not os.path.isfile(path) or os.path.abspath(path) in moved_sources:
                    continue
                rel = os.path.relpath(path, media.data_dir())
                if purge_orphans:
                    log(f"  orphan {'would be ' if dry_run else ''}deleted: {rel}")
                    if not dry_run:
                        os.remove(path)
                    summary["purged"] += 1
                else:
                    log(f"  orphan (left in place): {rel}")
                    summary["orphans"] += 1

        if not dry_run:
            _prune_empty_dirs(legacy_root)

    legacy_users_root = os.path.join(media.data_dir(), LEGACY_USERS_DIR)
    new_users_root = os.path.join(media.data_dir(), media.USERS_DIR)
    if (not dry_run and os.path.isdir(legacy_users_root)
            and os.path.realpath(legacy_users_root) != os.path.realpath(new_users_root)):
        _prune_empty_dirs(legacy_users_root)

    if not dry_run and summary["moved"]:
        from api.helpers.cover_bg_generator import regenerate_background
        for user in users:
            try:
                regenerate_background(user.id)
            except Exception as exc:  # collage is cosmetic; never fail the migration
                log(f"  collage regeneration failed for user {user.id}: {exc}")

    log(f"done: moved={summary['moved']} missing={summary['missing']} "
        f"orphans={summary['orphans']} purged={summary['purged']} users={summary['users']}"
        + (" (dry run, nothing written)" if dry_run else ""))
    return summary
