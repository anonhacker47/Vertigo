"""Habits: bought vs read per period, and the pace figures next to the chart."""
from datetime import date
from statistics import median

from api.insights.collection import Collection, as_naive, days_between
from api.insights.serializers import issue_basics, series_basics, iso

RANGES = ('ytd', 'last_year', 'all')


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

    bought_dates = [as_naive(i.bought_date) for i in collection.owned() if i.bought_date]
    read_rows = [(as_naive(i.read_date), i) for i in collection.all_issues if i.is_read and i.read_date]
    read_dates = [d for d, _ in read_rows]

    mode, buckets = _buckets(range_key, now, bought_dates, read_dates)

    candidates = collection.candidates()
    series_with_unread = sum(1 for f in collection.series if f.candidates())

    last_read = None
    if read_rows:
        d, issue = max(read_rows, key=lambda r: r[0])
        facts = collection.facts_for_issue(issue)
        last_read = {
            'issue': issue_basics(issue, facts),
            'series': series_basics(facts, now, dupes),
            'date': iso(d),
            'days': days_between(now, d),
        }

    gaps = []
    for i in collection.all_issues:
        if i.is_read and i.read_date and i.bought_date:
            gap = days_between(i.read_date, i.bought_date)
            if gap is not None and gap >= 0:
                gaps.append(gap)
    bought_to_read = {'median_days': int(median(gaps)), 'sample': len(gaps)} if len(gaps) >= 5 else None

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
            'last_read': last_read,
            'bought_to_read': bought_to_read,
            'waiting_longest': waiting_longest,
        },
    }
