"""Re-encode images stored before the WebP store; safe to run repeatedly."""
import os

from api import db
from api import media
from api.media.convert import EXT, sniff, to_webp
from api.models.issue import Issue
from api.models.user import User
from api.models.series_entities import Publisher, Creator, Character


def _rows(user):
    yield user, "profile_picture"
    for s in db.session.scalars(user.series_select()).all():
        yield s, "thumbnail"
    for i in db.session.scalars(Issue.select().where(Issue.user_id == user.id)).all():
        yield i, "thumbnail"
    for model in (Publisher, Creator, Character):
        for e in db.session.scalars(model.select().where(model.user_id == user.id)).all():
            yield e, "thumbnail"


def convert_media(dry_run: bool = False, log=print) -> dict:
    summary = {"converted": 0, "skipped": 0, "users": 0}
    for user in db.session.scalars(User.select()).all():
        summary["users"] += 1
        old_files = []
        for obj, column in _rows(user):
            db.session.refresh(obj)
            rel = getattr(obj, column)
            if not rel or rel.endswith(EXT):
                continue
            src = media.resolve(user.id, rel)
            if not src:
                continue
            with open(src, "rb") as fh:
                data = fh.read()
            try:
                _fmt, animated = sniff(data)
            except ValueError:
                animated = True
            if animated:
                summary["skipped"] += 1
                continue
            new_rel = os.path.splitext(rel)[0] + EXT
            log(f"  {rel}  ->  {new_rel}")
            summary["converted"] += 1
            if dry_run:
                continue
            dst = os.path.join(os.path.dirname(src), os.path.basename(new_rel))
            tmp = dst + ".part"
            with open(tmp, "wb") as fh:
                fh.write(to_webp(data))
            os.replace(tmp, dst)
            setattr(obj, column, new_rel)
            old_files.append(src)
        if dry_run:
            db.session.rollback()
            continue
        db.session.commit()
        for path in old_files:
            try:
                os.remove(path)
            except OSError:
                pass
    log(f"converted {summary['converted']} images for {summary['users']} users"
        f"{', skipped ' + str(summary['skipped']) + ' animated' if summary['skipped'] else ''}")
    return summary
