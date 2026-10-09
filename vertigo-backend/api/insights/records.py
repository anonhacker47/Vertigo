"""Firsts, records and the completed shelf. Everything here already happened."""
from collections import Counter
from datetime import date

from api.insights.collection import Collection, as_naive
from api.insights.serializers import issue_basics, series_basics, iso

RECORD_MINIMUM = 3
LONGEST_RUN_MINIMUM = 3


def _event(row, collection, dupes):
    when, issue, facts = row
    return {
        'issue': issue_basics(issue, facts),
        'series': series_basics(facts, collection.now, dupes),
        'date': iso(when),
    }


def _biggest_month(events, minimum=RECORD_MINIMUM):
    if not events:
        return None
    counts = Counter((when.year, when.month) for when, _, _ in events)
    best = max(counts.values())
    if best < minimum:
        return None
    year, month = max(k for k, v in counts.items() if v == best)
    return {'month': f'{year}-{month:02d}', 'label': date(year, month, 1).strftime('%b %Y'), 'count': best}


def _stamp(issues, attr, facts):
    dates = [as_naive(getattr(i, attr)) for i in issues]
    if dates and all(dates):
        return max(dates)
    return as_naive(facts.series.last_updated) or as_naive(facts.series.timestamp)


def build_records(collection: Collection, user) -> dict:
    now = collection.now
    dupes = collection.duplicate_titles()

    reads = [(as_naive(i.read_date), i, f) for f in collection.series
             for i in f.issues if i.is_read and i.read_date]
    buys = [(as_naive(i.bought_date), i, f) for f in collection.series
            for i in f.owned if i.bought_date]

    firsts = {
        'first_read': _event(min(reads, key=lambda r: r[0]), collection, dupes) if reads else None,
        'first_purchase': _event(min(buys, key=lambda r: r[0]), collection, dupes) if buys else None,
        'on_vertigo_since': iso(user.first_seen) if user is not None and user.first_seen else None,
    }

    complete_runs = [f for f in collection.series
                     if f.is_run and f.fully_collected and f.issue_count >= LONGEST_RUN_MINIMUM]
    longest = max(complete_runs, key=lambda f: f.issue_count) if complete_runs else None

    records = {
        'biggest_buying_month': _biggest_month(buys),
        'biggest_reading_month': _biggest_month(reads),
        'longest_complete_run': ({'series': series_basics(longest, now, dupes),
                                  'issue_count': longest.issue_count} if longest else None),
    }

    completed = []
    for f in collection.series:
        if not f.is_run:
            continue
        collected, read = f.fully_collected, f.fully_read
        if not (collected or read):
            continue
        collected_at = _stamp(f.owned, 'bought_date', f) if collected else None
        read_at = _stamp(f.read, 'read_date', f) if read else None
        completed_at = max(d for d in (collected_at, read_at) if d)
        completed.append({
            'series': series_basics(f, now, dupes),
            'status': 'both' if (collected and read) else ('collected' if collected else 'read'),
            'collected_at': iso(collected_at),
            'read_at': iso(read_at),
            'completed_at': iso(completed_at),
            '_sort': completed_at,
        })
    completed.sort(key=lambda c: c['_sort'], reverse=True)
    for c in completed:
        c.pop('_sort')

    singles = [f for f in collection.series if f.issue_count == 1]

    return {
        'firsts': firsts,
        'records': records,
        'completed': completed,
        'single_volumes': {
            'count': len(singles),
            'owned': sum(1 for f in singles if f.owned),
            'read': sum(1 for f in singles if f.read),
        },
    }
