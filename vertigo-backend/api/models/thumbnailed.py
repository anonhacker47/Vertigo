"""Thumbnail columns shared by series, issues and entities."""
from datetime import datetime, timezone

import sqlalchemy as sqla
from sqlalchemy import event, inspect


def _now():
    return datetime.now(timezone.utc)


class Thumbnailed:
    thumbnail = sqla.Column(sqla.String(280))
    thumbnail_updated = sqla.Column(sqla.DateTime)

    def touch_thumbnail(self):
        """Mark the image as changed; the path may be unchanged."""
        self.thumbnail_updated = _now()


@event.listens_for(Thumbnailed, 'before_insert', propagate=True)
def _stamp_new_thumbnail(mapper, connection, target):
    if target.thumbnail and target.thumbnail_updated is None:
        target.thumbnail_updated = _now()


@event.listens_for(Thumbnailed, 'before_update', propagate=True)
def _stamp_changed_thumbnail(mapper, connection, target):
    # Path changes only; a file replaced in place needs touch_thumbnail().
    if inspect(target).attrs.thumbnail.history.has_changes():
        target.thumbnail_updated = _now()
