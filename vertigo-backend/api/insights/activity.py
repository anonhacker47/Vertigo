"""Activity: bought vs read per period, and the figures above the chart."""
from datetime import date

from api.insights.collection import Collection, as_naive, days_between
from api.insights.serializers import issue_basics, series_basics, iso

RANGES = ('ytd', 'last_year', 'all')


def _latest(rows, collection, now, dupes):
    """The most recent (date, issue) row as a figure, or None."""
    if not rows:
        return None
    d, issue = max(rows, key=lambda r: r[0])
    facts = collection.facts_for_issue(issue)
    return {
        'issue': issue_basics(issue, facts),
        'series': series_basics(facts, now, dupes),
        'date': iso(d),
        'days': days_between(now, d),
    }


def _buckets(range_key, now, bought_dates, read_dates):
    if range_key == 'all':
        years = sorted({d.year for d in bought_dates + read_dates})
        start = years[0] if years else now.year
        out = []
        for y in range(start, now.year + 1):
            out.append({
                'key': str(y), 'label': str(y),
                'bought': sum(1 for d in bought_dates if d.year == y),
                'read': sum(1 for d in read_dates if d.year == y),
            })
        return 'year', out

    if range_key == 'ytd':
        keys = [(now.year, m) for m in range(1, now.month + 1)]
    else:
        keys = [(now.year - 1, m) for m in range(1, 13)]
    out = []
    for y, m in keys:
        out.append({
            'key': f'{y}-{m:02d}', 'label': date(y, m, 1).strftime('%b %Y'),
            'bought': sum(1 for d in bought_dates if (d.year, d.month) == (y, m)),
            'read': sum(1 for d in read_dates if (d.year, d.month) == (y, m)),
        })
    return 'month', out


def build_activity(collection: Collection, range_key: str = 'ytd') -> dict:
    if range_key not in RANGES:
        range_key = 'ytd'
    now = collection.now
    dupes = collection.duplicate_titles()

    bought_rows = [(as_naive(i.bought_date), i) for i in collection.owned() if i.bought_date]
    read_rows = [(as_naive(i.read_date), i) for i in collection.all_issues if i.is_read and i.read_date]
    bought_dates = [d for d, _ in bought_rows]
    read_dates = [d for d, _ in read_rows]

    mode, buckets = _buckets(range_key, now, bought_dates, read_dates)

    candidates = collection.candidates()
    series_with_unread = sum(1 for f in collection.series if f.candidates())

    # a purchase dated ahead is a pre-order, not bought yet
    last_bought = _latest([r for r in bought_rows if r[0] <= now], collection, now, dupes)
    last_read = _latest(read_rows, collection, now, dupes)

    waiting_longest = None
    dated = [i for i in candidates if i.bought_date]
    if dated:
        issue = min(dated, key=lambda i: as_naive(i.bought_date))
        facts = collection.facts_for_issue(issue)
        waiting_longest = {
            'issue': issue_basics(issue, facts),
            'series': series_basics(facts, now, dupes),
            'since': iso(issue.bought_date),
            'days': days_between(now, issue.bought_date),
        }

    return {
        'range': range_key,
        'mode': mode,
        'buckets': buckets,
        'totals': {
            'bought': sum(b['bought'] for b in buckets),
            'read': sum(b['read'] for b in buckets),
        },
        'figures': {
            'unread': {'count': len(candidates), 'series_count': series_with_unread},
            'last_bought': last_bought,
            'last_read': last_read,
            'waiting_longest': waiting_longest,
        },
    }
