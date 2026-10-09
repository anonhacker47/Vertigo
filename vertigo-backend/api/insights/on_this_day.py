"""'something that happened on today's date in an earlier year.
"""
from datetime import date, timedelta

from api.insights.collection import Collection, as_naive
from api.insights.serializers import issue_basics, series_basics, iso
from api.insights.up_next import issue_label

NEAR_DAYS = 3
MAX_GROUPS = 2


def _same_year_date(event_date: date, year: int) -> date:
    try:
        return event_date.replace(year=year)
    except ValueError:  # 29 Feb
        return event_date.replace(year=year, day=28)


def build_on_this_day(collection: Collection, user):
    now = collection.now
    today = now.date()
    dupes = collection.duplicate_titles()

    events = []
    for f in collection.series:
        for i in f.owned:
            if i.bought_date:
                events.append(('bought', as_naive(i.bought_date).date(), i, f))
        for i in f.issues:
            if i.is_read and i.read_date:
                events.append(('read', as_naive(i.read_date).date(), i, f))
    events = [e for e in events if e[1].year < today.year]

    exact = [e for e in events if (e[1].month, e[1].day) == (today.month, today.day)]
    if exact:
        scope, pool = 'day', exact
    else:
        pool = []
        for e in events:
            shifted = _same_year_date(e[1], today.year)
            if abs((shifted - today).days) <= NEAR_DAYS:
                pool.append(e)
        scope = 'week' if pool else None

    groups = []
    if pool:
        keyed = {}
        for kind, when, issue, facts in pool:
            keyed.setdefault((kind, when.year), []).append((when, issue, facts))
        for (kind, year), rows in sorted(keyed.items(), key=lambda kv: kv[0][1], reverse=True)[:MAX_GROUPS]:
            rows.sort(key=lambda r: r[0])
            groups.append({
                'kind': kind,
                'year': year,
                'date': rows[0][0].isoformat(),
                'count': len(rows),
                'items': [{
                    'label': issue_label(issue, facts, dupes, now),
                    'issue': issue_basics(issue, facts),
                    'series': series_basics(facts, now, dupes),
                } for _, issue, facts in rows[:3]],
            })

    anniversary = None
    if user is not None and user.first_seen:
        first = as_naive(user.first_seen).date()
        if first.year < today.year and (first.month, first.day) == (today.month, today.day):
            anniversary = {'years': today.year - first.year, 'since': iso(user.first_seen)}

    if not groups and not anniversary:
        return None
    return {'scope': scope or 'day', 'groups': groups, 'anniversary': anniversary}
