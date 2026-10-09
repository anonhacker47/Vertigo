"""a registry of small facts, each skipped when its data is missing.

"""
import random
from collections import Counter
from colorsys import rgb_to_hls
from datetime import datetime

from api.insights.collection import Collection, as_naive, days_between
from api.insights.relative import span_text
from api.insights.serializers import issue_basics, series_basics, issue_cover, series_cover, parse_rgb
from api.insights.up_next import issue_label

SHOW = 5
MIN_SHOW = 2
PINNED = 'shelf_colour'

HUE_FAMILIES = (
    ('red', 345, 375), ('orange', 15, 45), ('yellow', 45, 70), ('green', 70, 165),
    ('teal', 165, 200), ('blue', 200, 260), ('purple', 260, 300), ('pink', 300, 345),
)


def _fmt_month(dt):
    return as_naive(dt).strftime('%b %Y')


def _fmt_day(dt):
    d = as_naive(dt)
    return f'{d.day} {d.strftime("%b %Y")}'


def _series_link(facts):
    return {'kind': 'series', 'id': facts.series.id, 'slug': facts.series.slug}


def _issue_link(issue, facts):
    return {'kind': 'issue', 'series_id': facts.series.id, 'slug': facts.series.slug, 'number': issue.number}


def _label(issue, facts, ctx):
    return issue_label(issue, facts, ctx['dupes'], ctx['now'])


# ------------------------------------------------------------------------- facts

def this_year(col: Collection, ctx):
    now, year = col.now, col.now.year
    bought = [i for i in col.owned() if i.bought_date and as_naive(i.bought_date).year == year]
    read = [i for i in col.all_issues if i.is_read and i.read_date and as_naive(i.read_date).year == year]
    finished = [f for f in col.series if f.is_run and f.fully_read
                and f.last_read_at and f.last_read_at.year == year]
    if not (bought or read):
        return None
    latest = max(read, key=lambda i: as_naive(i.read_date)) if read else None
    facts = col.facts_for_issue(latest) if latest else None
    runs = f'{len(finished)} run{"s" if len(finished) != 1 else ""} finished'
    return {
        'id': 'this_year', 'kicker': f'{year} so far',
        'headline': f'{len(bought)} bought, {len(read)} read, {runs}',
        'detail': (f'Latest read: {_label(latest, facts, ctx)}, '
                   f'{span_text(days_between(now, latest.read_date))} ago.' if latest
                   else 'Nothing read yet this year.'),
        'cover': issue_cover(latest, facts.series) if latest else None,
        'link': _issue_link(latest, facts) if latest else None,
    }


def finish_rate(col, ctx):
    started = [f for f in col.series if f.is_run and f.read]
    if len(started) < 5:
        return None
    done = [f for f in started if f.fully_read]
    pct = round(100 * len(done) / len(started))
    latest = max(done, key=lambda f: f.last_read_at or col.now) if done else None
    return {
        'id': 'finish_rate', 'kicker': 'Runs',
        'headline': 'You finish what you start' if pct >= 60 else f'You finish {pct}% of what you start',
        'detail': f'{len(done)} of {len(started)} runs read to the end.',
        'cover': series_cover(latest.series) if latest else None,
        'link': _series_link(latest) if latest else None,
    }


def unstarted_series(col, ctx):
    rows = [f for f in col.series if f.issues and not f.owned]
    if not rows:
        return None
    rows.sort(key=lambda f: as_naive(f.series.timestamp) or col.now, reverse=True)
    titles = [series_basics(f, col.now, ctx['dupes'])['display_title'] for f in rows]
    if len(titles) > 2:
        names = f'{titles[0]}, {titles[1]} and {len(titles) - 2} more.'
    else:
        names = ' and '.join(titles) + '.'
    return {
        'id': 'unstarted_series', 'kicker': 'Not started',
        'headline': f'{len(rows)} series with nothing bought yet',
        'detail': names,
        'cover': series_cover(rows[0].series),
        'link': {'kind': 'collection'},
    }


def top_creator(col, ctx):
    per_creator = {}
    for f in col.series:
        if not f.owned:
            continue
        for c in f.creators:
            per_creator.setdefault(c.id, {'creator': c, 'series': [], 'books': 0})
            per_creator[c.id]['series'].append(f)
            per_creator[c.id]['books'] += len(f.owned)
    ranked = sorted(per_creator.values(), key=lambda r: (len(r['series']), r['books']), reverse=True)
    if not ranked or len(ranked[0]['series']) < 3:
        return None
    top = ranked[0]
    second = len(ranked[1]['series']) if len(ranked) > 1 else 0
    if second == len(top['series']):
        if len(ranked) > 2 and len(ranked[2]['series']) == second:
            return None
        names = f"{top['creator'].title} and {ranked[1]['creator'].title}"
        headline = f'{names} tie at {len(top["series"])} series'
    else:
        headline = f"{top['creator'].title} is all over your shelf"
    best = max(top['series'], key=lambda f: len(f.owned))
    return {
        'id': 'top_creator', 'kicker': 'Creators',
        'headline': headline,
        'detail': f"{len(top['series'])} series, {top['books']} books. {best.series.title} most of all.",
        'cover': series_cover(best.series),
        'link': {'kind': 'creator', 'id': top['creator'].id, 'slug': top['creator'].slug},
    }


def _family(hue_deg):
    h = hue_deg % 360
    for name, lo, hi in HUE_FAMILIES:
        if lo <= h < hi or lo <= h + 360 < hi:
            return name
    return 'red'


def shelf_colour(col, ctx):
    chromatic = []
    for f in col.series:
        rgb = parse_rgb(f.series.dominant_color)
        if not rgb:
            continue
        r, g, b = (c / 255 for c in rgb)
        h, l, s = rgb_to_hls(r, g, b)
        if s >= 0.25 and 0.12 <= l <= 0.88:
            chromatic.append((f, _family(h * 360), s, rgb))
    if len(chromatic) < 8:
        return None
    counts = Counter(fam for _, fam, _, _ in chromatic)
    family, n = counts.most_common(1)[0]
    if n / len(chromatic) < 0.25:
        return None
    swatches = sorted((c for c in chromatic if c[1] == family), key=lambda c: c[2], reverse=True)[:3]
    return {
        'id': 'shelf_colour', 'kicker': 'Shelf colour',
        'headline': f'Your shelf leans {family}',
        'detail': f'{n} of the {len(chromatic)} covers with a clear colour are mostly {family}.',
        'cover': None,
        'swatches': ['#%02x%02x%02x' % rgb for _, _, _, rgb in swatches],
        'link': {'kind': 'collection'},
    }


def top_publisher(col, ctx):
    per_pub = {}
    owned_series = [f for f in col.series if f.owned]
    for f in owned_series:
        if f.publisher:
            per_pub.setdefault(f.publisher.id, {'publisher': f.publisher, 'series': 0, 'books': 0})
            per_pub[f.publisher.id]['series'] += 1
            per_pub[f.publisher.id]['books'] += len(f.owned)
    if len(per_pub) < 2:
        return None
    top = max(per_pub.values(), key=lambda r: (r['series'], r['books']))
    if top['series'] < 3:
        return None
    return {
        'id': 'top_publisher', 'kicker': 'Publishers',
        'headline': f"Mostly {top['publisher'].title}",
        'detail': f"{top['series']} of your {len(owned_series)} series with an owned book.",
        'cover': None,
        'link': {'kind': 'publisher', 'id': top['publisher'].id, 'slug': top['publisher'].slug},
    }


def _pairs(col):
    out = []
    for f in col.series:
        for i in f.issues:
            if i.is_read and i.read_date and i.bought_date:
                out.append((days_between(i.read_date, i.bought_date), i, f))
    return out


def read_before_bought(col, ctx):
    rows = [p for p in _pairs(col) if p[0] <= -7]
    if not rows:
        return None
    gap, issue, facts = min(rows, key=lambda p: p[0])
    extra = f' And {len(rows) - 1} other{"s" if len(rows) > 2 else ""}.' if len(rows) > 1 else ''
    return {
        'id': 'read_before_bought', 'kicker': 'Read first, bought later',
        'headline': f'You read {_label(issue, facts, ctx)} {span_text(gap)} before buying it',
        'detail': f'Read {_fmt_month(issue.read_date)}, bought {_fmt_month(issue.bought_date)}.{extra}',
        'cover': issue_cover(issue, facts.series),
        'link': _issue_link(issue, facts),
    }


def longest_wait_to_read(col, ctx):
    rows = [p for p in _pairs(col) if p[0] > 0]
    if len(rows) < 5:
        return None
    gap, issue, facts = max(rows, key=lambda p: p[0])
    return {
        'id': 'longest_wait_to_read', 'kicker': 'Patience',
        'headline': f'{_label(issue, facts, ctx)} waited {span_text(gap)}',
        'detail': f'Bought {_fmt_month(issue.bought_date)}, read {_fmt_month(issue.read_date)}.',
        'cover': issue_cover(issue, facts.series),
        'link': _issue_link(issue, facts),
    }


def fastest_read(col, ctx):
    rows = [p for p in _pairs(col) if p[0] >= 0]
    if len(rows) < 5:
        return None
    gap, issue, facts = min(rows, key=lambda p: (p[0], -as_naive(p[1].read_date).timestamp()))
    when = 'the same day' if gap == 0 else ('a day' if gap == 1 else f'{gap} days')
    return {
        'id': 'fastest_read', 'kicker': 'No waiting',
        'headline': f'{_label(issue, facts, ctx)}: bought and read in {when}',
        'detail': f'Bought {_fmt_day(issue.bought_date)}, read {_fmt_day(issue.read_date)}.',
        'cover': issue_cover(issue, facts.series),
        'link': _issue_link(issue, facts),
    }


def single_volume_share(col, ctx):
    total = len(col.series)
    singles = [f for f in col.series if f.issue_count == 1]
    if total < 10 or len(singles) / total < 0.30:
        return None
    read = sum(1 for f in singles if f.read)
    latest = max((f for f in singles if f.owned), key=lambda f: f.last_bought_at() or col.now, default=None)
    share = len(singles) / total
    return {
        'id': 'single_volume_share', 'kicker': 'Formats',
        'headline': 'Half your shelf is one-and-done' if share >= 0.45 else f'{len(singles)} single volumes',
        'detail': f'{len(singles)} of {total} series are single volumes; {read} read.',
        'cover': series_cover(latest.series) if latest else None,
        'link': _series_link(latest) if latest else {'kind': 'collection'},
    }


def longest_run(col, ctx):
    rows = [f for f in col.series if f.owned and f.issue_count >= 5]
    if not rows:
        return None
    top = max(rows, key=lambda f: f.issue_count)
    return {
        'id': 'longest_run', 'kicker': 'Runs',
        'headline': f'Longest run: {top.series.title}',
        'detail': f'{top.issue_count} issues, {len(top.owned)} owned.',
        'cover': series_cover(top.series),
        'link': _series_link(top),
    }


def format_lean(col, ctx):
    if len(col.series) < 5:
        return None
    counts = Counter((f.series.series_format or '').strip() for f in col.series if f.series.series_format)
    if not counts:
        return None
    fmt, n = counts.most_common(1)[0]
    if n / len(col.series) < 0.40:
        return None
    latest = max((f for f in col.series if (f.series.series_format or '').strip() == fmt and f.owned),
                 key=lambda f: f.last_bought_at() or col.now, default=None)
    plural = fmt.lower() + ('' if fmt.lower().endswith('s') else 's')
    return {
        'id': 'format_lean', 'kicker': 'Formats',
        'headline': f'{fmt} collector',
        'detail': f'{n} of {len(col.series)} series are {plural}.',
        'cover': series_cover(latest.series) if latest else None,
        'link': _series_link(latest) if latest else {'kind': 'collection'},
    }


def manga_share(col, ctx):
    manga = [f for f in col.series if f.is_manga]
    if not manga or len(col.series) < 5:
        return None
    titles = [f.series.title for f in manga[:4]]
    return {
        'id': 'manga_share', 'kicker': 'Manga',
        'headline': f'Manga: {len(manga)} of {len(col.series)} series',
        'detail': ', '.join(titles) + ('.' if len(manga) <= 4 else f' and {len(manga) - 4} more.'),
        'cover': series_cover(manga[0].series),
        'link': _series_link(manga[0]),
    }


# ranked by usefulness: to-do first, identity second, trivia last
REGISTRY = (
    this_year, finish_rate, unstarted_series, top_creator, shelf_colour, top_publisher,
    read_before_bought, longest_wait_to_read, fastest_read, single_volume_share, longest_run,
    format_lean, manga_share,
)


def _weighted_sample(rng, items, weights, k):
    items, weights = list(items), list(weights)
    out = []
    while items and len(out) < k:
        total = sum(weights)
        r = rng.random() * total
        acc = 0
        for idx, w in enumerate(weights):
            acc += w
            if r <= acc:
                out.append(items.pop(idx))
                weights.pop(idx)
                break
    return out


def build_facts(collection: Collection, user) -> list:
    ctx = {'now': collection.now, 'dupes': collection.duplicate_titles()}
    eligible = []
    for rank, fn in enumerate(REGISTRY, start=1):
        fact = fn(collection, ctx)
        if fact:
            fact['rank'] = rank
            eligible.append(fact)
    if len(eligible) < MIN_SHOW:
        return []

    seed = f'{collection.user_id}:{collection.now.date().isoformat()}'
    rng = random.Random(seed)

    chosen = [f for f in eligible if f['id'] == PINNED]
    pool = [f for f in eligible if f['id'] != PINNED]
    picked = _weighted_sample(rng, pool, [1 / f['rank'] for f in pool], SHOW - len(chosen))
    chosen.extend(picked)

    if not any(f['rank'] <= 3 for f in chosen):
        top = next((f for f in eligible if f['rank'] <= 3), None)
        if top:
            chosen[-1] = top

    chosen.sort(key=lambda f: (0 if f['id'] == PINNED else 1, f['rank']))
    for f in chosen:
        f.pop('rank', None)
    return chosen
