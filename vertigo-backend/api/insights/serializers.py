import re
from datetime import datetime
from typing import Optional

from flask import url_for

from api.insights.collection import SeriesFacts, as_naive


def iso(dt: Optional[datetime]) -> Optional[str]:
    dt = as_naive(dt)
    return dt.isoformat(timespec='seconds') + 'Z' if dt else None


def month_key(dt: datetime) -> str:
    return as_naive(dt).strftime('%Y-%m')


def parse_rgb(value) -> Optional[tuple]:
    """``Series.dominant_color`` is stored as text like ``(17, 89, 204)``."""
    if not value:
        return None
    nums = [int(n) for n in re.findall(r'\d+', str(value))[:3]]
    if len(nums) != 3:
        return None
    return tuple(min(255, max(0, n)) for n in nums)


def rgb_hex(rgb: Optional[tuple]) -> Optional[str]:
    return '#%02x%02x%02x' % rgb if rgb else None


def _bust(dt: Optional[datetime]) -> Optional[int]:
    dt = as_naive(dt)
    return int(dt.timestamp() * 1000) if dt else None


def series_cover(series) -> str:
    return url_for('series.get_series_image', id=series.id, _external=True,
                   t=_bust(series.last_updated))


def issue_cover(issue, series) -> str:
    if issue.thumbnail:
        return url_for('issue.get_issue_image', id=issue.id, _external=True,
                       t=_bust(issue.last_updated))
    return series_cover(series)


def series_basics(facts: SeriesFacts, now: datetime, duplicate_titles=frozenset()) -> dict:
    s = facts.series
    title = s.title or ''
    display_title = title
    if title.strip().lower() in duplicate_titles and s.series_format:
        display_title = f'{title} ({s.series_format})'
    return {
        'id': s.id,
        'title': title,
        'display_title': display_title,
        'slug': s.slug,
        'series_format': s.series_format,
        'manga': facts.is_manga,
        'is_run': facts.is_run,
        'issue_count': facts.issue_count,
        'owned_count': len(facts.owned),
        'read_count': len(facts.read),
        'publisher': facts.publisher.title if facts.publisher else None,
        'dominant_color': rgb_hex(parse_rgb(s.dominant_color)),
        'cover': series_cover(s),
    }


def issue_basics(issue, facts: SeriesFacts) -> dict:
    return {
        'id': issue.id,
        'number': issue.number,
        'title': issue.title,
        'is_owned': bool(issue.is_owned),
        'is_read': bool(issue.is_read),
        'bought_date': iso(issue.bought_date),
        'read_date': iso(issue.read_date),
        'cover': issue_cover(issue, facts.series),
    }


def run_strip(facts: SeriesFacts, now: datetime) -> list:
    """One entry per issue, in number order: read | owned | missing."""
    out = []
    for i in facts.issues:
        if i.is_read:
            state = 'read'
        elif i.is_owned:
            state = 'owned'
        else:
            state = 'missing'
        out.append({'number': i.number, 'state': state})
    return out
