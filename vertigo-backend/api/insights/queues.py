"""The two to-do lists: what is pending to read, and which run to get next."""
from api.insights.collection import Collection, as_naive
from api.insights.ranking import ranked, finishes_run, queue_marker
from api.insights.serializers import issue_basics, series_basics, run_strip, iso


def build_reading_queue(collection: Collection, exclude_series_id=None) -> dict:
    """Series with an in-hand unread issue, ranked like the hero, hero's series excluded."""
    now = collection.now
    dupes = collection.duplicate_titles()

    total_unread = 0
    series_with_unread = 0
    for facts in collection.series:
        n = len(facts.candidates())
        if n:
            total_unread += n
            series_with_unread += 1

    items = []
    for tier, issue, facts in ranked(collection):
        if facts.series.id == exclude_series_id:
            continue
        marker, marker_date = queue_marker(facts, now)
        items.append({
            'series': series_basics(facts, now, dupes),
            'next_issue': issue_basics(issue, facts),
            'tier': tier,
            'unread_count': len(facts.candidates()),
            'finishes_run': finishes_run(facts),
            'marker': marker,
            'marker_date': iso(marker_date),
            'last_read_at': iso(facts.last_read_at),
            'run': run_strip(facts, now),
        })

    return {
        'total_unread': total_unread,
        'series_count': series_with_unread,
        'items': items,
    }


def build_get_next(collection: Collection) -> dict:
    """Started-but-incomplete runs, closest to done first."""
    now = collection.now
    dupes = collection.duplicate_titles()

    items = []
    for facts in collection.series:
        owned, missing = facts.owned, facts.missing
        if not owned or not missing:
            continue
        caught_up = all(i.is_read for i in owned)
        last_bought = facts.last_bought_at()
        items.append({
            'series': series_basics(facts, now, dupes),
            'missing_count': len(missing),
            'next_missing': min(i.number for i in missing),
            'caught_up': caught_up,
            'unread_on_shelf': len(facts.candidates()),
            'last_bought': iso(last_bought),
            '_sort': (len(missing), 0 if caught_up else 1,
                      -(as_naive(last_bought).timestamp() if last_bought else 0),
                      (facts.series.title or '').lower()),
            'run': run_strip(facts, now),
        })
    items.sort(key=lambda x: x['_sort'])
    for item in items:
        item.pop('_sort')

    unstarted = [f for f in collection.series if f.issues and not f.owned]
    unstarted.sort(key=lambda f: as_naive(f.series.timestamp) or now, reverse=True)

    return {
        'one_away': sum(1 for i in items if i['missing_count'] == 1),
        'items': items,
        'unstarted': {
            'count': len(unstarted),
            'titles': [series_basics(f, now, dupes)['display_title'] for f in unstarted[:3]],
        },
    }
