"""The rule that orders the reading side of the page.

    1a  continue   you read #n and #n+1 is on the shelf; last read within a year
    2a  start      nothing read, #1 owned and bought within 30 days (fresh)
    1b  stalled    a continuation whose last read is over a year old
    2b  unstarted  nothing read, #1 owned, not fresh
    3   backfill   any other candidate (a gap below, or an issue you skipped)

Order: 1a, 2a, 1b, 2b, 3. A run you touched this year beats a fresh purchase; a fresh
purchase beats a run you abandoned a year ago.
"""
from datetime import datetime
from typing import Optional, Tuple

from api.insights.collection import SeriesFacts, as_naive, days_between

TIER_ORDER = ('1a', '2a', '1b', '2b', '3')
STALLED_AFTER_DAYS = 365
FRESH_WITHIN_DAYS = 30
QUEUE_STALLED_AFTER_DAYS = 90


def pick(facts: SeriesFacts, now: datetime) -> Optional[Tuple[str, object]]:
    """The (tier, issue) a series puts forward, or None when it has no candidate."""
    candidates = facts.candidates()
    if not candidates:
        return None
    by_number = {i.number: i for i in candidates}

    last = facts.last_read_number
    if last is not None:
        nxt = facts.next_number_after_last_read
        if nxt in by_number:
            since = days_between(now, facts.last_read_at)
            recent = since is not None and since <= STALLED_AFTER_DAYS
            return ('1a' if recent else '1b'), by_number[nxt]

    if not facts.read and facts.first_number in by_number:
        first = by_number[facts.first_number]
        bought = days_between(now, first.bought_date)
        fresh = bought is not None and 0 <= bought <= FRESH_WITHIN_DAYS
        return ('2a' if fresh else '2b'), first

    return '3', min(candidates, key=lambda i: i.number)


def finishes_run(facts: SeriesFacts) -> bool:
    return facts.is_run and len(facts.read) + 1 == facts.issue_count


def _neg_ts(dt: Optional[datetime], missing=float('inf')) -> float:
    dt = as_naive(dt)
    return -dt.timestamp() if dt else missing


def sort_key(tier: str, issue, facts: SeriesFacts):
    """Smaller sorts first. Shapes only need to agree within a tier."""
    ti = TIER_ORDER.index(tier)
    finishes = 0 if finishes_run(facts) else 1
    last_read = _neg_ts(facts.last_read_at, 0)
    bought = _neg_ts(issue.bought_date)
    added = _neg_ts(facts.series.timestamp, 0)
    progress = -(len(facts.read) / facts.issue_count) if facts.issue_count else 0
    if tier == '1a':
        return (ti, last_read, finishes, progress, issue.number)
    if tier == '2a':
        return (ti, bought, added, issue.number)
    if tier == '1b':
        return (ti, finishes, last_read, issue.number)
    if tier == '2b':
        return (ti, bought, added, issue.number)
    return (ti, bought, added, issue.number)


def ranked(collection):
    """[(tier, issue, facts)] for every series with a candidate, best first."""
    entries = []
    for facts in collection.series:
        choice = pick(facts, collection.now)
        if choice:
            tier, issue = choice
            entries.append((tier, issue, facts))
    entries.sort(key=lambda e: sort_key(e[0], e[1], e[2]))
    return entries


def queue_marker(facts: SeriesFacts, now: datetime):
    """(marker, date) for a reading-queue row: fresh > stalled > not_started > None."""
    candidates = facts.candidates()
    fresh = [as_naive(i.bought_date) for i in candidates
             if i.bought_date and 0 <= (days_between(now, i.bought_date) or 0) <= FRESH_WITHIN_DAYS]
    if fresh:
        return 'fresh', max(fresh)
    last_read_at = facts.last_read_at
    if facts.read:
        if last_read_at and days_between(now, last_read_at) > QUEUE_STALLED_AFTER_DAYS:
            return 'stalled', last_read_at
        return None, last_read_at
    dated = [as_naive(i.bought_date) for i in candidates if i.bought_date]
    return 'not_started', (min(dated) if dated else as_naive(facts.series.timestamp))
