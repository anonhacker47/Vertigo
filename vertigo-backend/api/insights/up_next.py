from api.insights.collection import Collection, SeriesFacts, days_between
from api.insights.ranking import ranked, finishes_run
from api.insights.relative import relative_time
from api.insights.serializers import issue_basics, series_basics


def issue_label(issue, facts: SeriesFacts, duplicate_titles, now) -> str:
    """'Series #4' for a run; a single volume is just its series title."""
    title = series_basics(facts, now, duplicate_titles)['display_title']
    return title if not facts.is_run else f'{title} #{issue.number}'


def reason_line(tier: str, issue, facts: SeriesFacts, now) -> str:
    last = facts.last_read_number
    n = issue.number
    if tier == '1a':
        since = relative_time(days_between(now, facts.last_read_at) or 0)
        if finishes_run(facts):
            return f'You read #{last}, {since}. #{n} finishes the run.'
        return f'You read {facts.series.title} #{last}, {since}. #{n} is on the shelf.'
    if tier == '1b':
        since = relative_time(days_between(now, facts.last_read_at) or 0)
        if finishes_run(facts):
            return f'One more and {facts.series.title} is done. You stopped at #{last} {since}.'
        waiting = relative_time(days_between(now, issue.bought_date)) if issue.bought_date else None
        if waiting:
            return f'You stopped at #{last} {since}. #{n} has been waiting since {waiting.replace(" ago", "")}.'
        return f'You stopped at #{last} {since}. #{n} is on the shelf.'
    if tier == '2a':
        bought = relative_time(days_between(now, issue.bought_date) or 0).capitalize()
        if facts.is_run:
            return f'Bought {bought.lower()}. Nothing read in {facts.series.title} yet.'
        return f'Bought {bought.lower()}. Not read yet.'
    if tier == '2b':
        if issue.bought_date:
            since = relative_time(days_between(now, issue.bought_date) or 0)
            return f'On the shelf since {since.replace(" ago", "")}. Unread.'
        added = relative_time(days_between(now, facts.series.timestamp) or 0)
        return f'Added {added}. Nothing read yet.'
    # tier 3: a gap below, or something skipped
    missing_below = [i.number for i in facts.missing if i.number < n]
    if missing_below:
        return f'#{n} is on the shelf, but #{min(missing_below)} isn\'t.'
    if last is not None and n < last:
        return f'You\'re past #{n} (read up to #{last}), but it\'s still unread.'
    return f'#{n} is on the shelf. Unread.'


def build_up_next(collection: Collection) -> dict:
    now = collection.now
    dupes = collection.duplicate_titles()

    if not collection.series:
        return {'state': 'no_series', 'hero': None, 'on_deck': []}
    if not any(f.owned for f in collection.series):
        return {'state': 'nothing_owned', 'hero': None, 'on_deck': [],
                'series_count': len(collection.series)}

    entries = ranked(collection)
    if not entries:
        return {'state': 'nothing_unread', 'hero': None, 'on_deck': []}

    def entry(tier, issue, facts):
        return {
            'tier': tier,
            'finishes_run': finishes_run(facts),
            'reason': reason_line(tier, issue, facts, now),
            'label': issue_label(issue, facts, dupes, now),
            'issue': issue_basics(issue, facts),
            'series': series_basics(facts, now, dupes),
        }

    hero_facts = entries[0][2]
    hero = entry(*entries[0])
    on_deck = []
    for t, i, f in entries[1:]:
        if f is hero_facts:
            continue
        on_deck.append(entry(t, i, f))
        if len(on_deck) == 2:
            break
    return {'state': 'ok', 'hero': hero, 'on_deck': on_deck}
