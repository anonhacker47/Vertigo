"""Status filters of the collection: one condition per value a client may send."""
import sqlalchemy as sqla
from flask import abort

from api.models.series import Series

_issues = sqla.func.coalesce(Series.issue_count, 0)
_owned = sqla.func.coalesce(Series.owned_count, 0)
_read = sqla.func.coalesce(Series.read_count, 0)
_all_owned = sqla.and_(_issues > 0, _owned >= _issues)
_all_read = sqla.and_(_issues > 0, _read >= _issues)

SERIES_FILTERS = {
    'collection': {
        'owned': _owned > 0,
        'not_owned': _owned == 0,
        'complete': _all_owned,
        'incomplete': sqla.and_(_owned > 0, sqla.not_(_all_owned)),
    },
    'reading': {
        'unread': _read == 0,
        'in_progress': sqla.and_(_read > 0, sqla.not_(_all_read)),
        'read': _all_read,
    },
    'type': {
        'manga': Series.manga.is_(True),
        'comic': Series.manga.isnot(True),
    },
}


def apply_status_filters(qs, args):
    """Narrow the select by the status filters in the query string; unknown values are a 400."""
    for name, choices in SERIES_FILTERS.items():
        value = args.get(name)
        if not value:
            continue
        if value not in choices:
            abort(400, f'Cannot filter {name} by {value!r}.')
        qs = qs.filter(choices[value])

    min_rating = args.get('min_rating')
    if min_rating:
        try:
            min_rating = float(min_rating)
        except ValueError:
            abort(400, f'Cannot filter by a minimum rating of {min_rating!r}.')
        qs = qs.filter(Series.user_rating >= min_rating)
    return qs
