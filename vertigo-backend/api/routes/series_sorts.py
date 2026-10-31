"""What the collection can be sorted by: one column or expression per key a client may send."""
import sqlalchemy as sqla

from api.models import associations
from api.models.issue import Issue
from api.models.series import Series
from api.models.series_entities import Publisher


def _latest(column):
    """The newest value of an issue column within the series; null when it has none."""
    return (sqla.select(sqla.func.max(column))
            .where(Issue.series_id == Series.id)
            .correlate(Series).scalar_subquery())


def _share(part, whole):
    """part / whole as a fraction, 0 when there is nothing to divide by."""
    return sqla.func.coalesce(sqla.cast(part, sqla.Float) / sqla.func.nullif(whole, 0), 0.0)


def _count(column):
    return sqla.func.coalesce(column, 0)


_first_publisher = (sqla.select(sqla.func.min(Publisher.title))
                    .select_from(associations.series_publisher)
                    .join(Publisher, Publisher.id == associations.series_publisher.c.publisher_id)
                    .where(associations.series_publisher.c.series_id == Series.id)
                    .correlate(Series).scalar_subquery())

SERIES_SORTS = {
    'title': Series.title,
    'publisher': _first_publisher,
    'series_format': Series.series_format,
    'timestamp': Series.timestamp,
    'issue_count': _count(Series.issue_count),
    'owned_count': _count(Series.owned_count),
    'collected': _share(Series.owned_count, Series.issue_count),
    'read': _share(Series.read_count, Series.owned_count),
    'missing': _count(Series.issue_count) - _count(Series.owned_count),
    'unread': _count(Series.owned_count) - _count(Series.read_count),
    'last_bought': _latest(Issue.bought_date),
    'last_read': _latest(Issue.read_date),
    'user_rating': Series.user_rating,
    'purchase_cost': _count(Series.purchase_cost),
}
