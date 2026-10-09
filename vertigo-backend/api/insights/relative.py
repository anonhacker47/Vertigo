"""Relative-time and span wording shared by the copy the insights endpoints produce. """


def _unit(days: int):
    if days < 14:
        return days, 'day'
    if days < 60:
        return max(2, round(days / 7)), 'week'
    if days < 365:
        return max(2, round(days / 30.4)), 'month'
    if days < 548:
        return 1, 'year'
    return max(2, round(days / 365.25)), 'year'


def relative_time(days: int) -> str:
    """Whole days from today (positive = past, negative = future) as words."""
    if days == 0:
        return 'today'
    if days == 1:
        return 'yesterday'
    if days == -1:
        return 'tomorrow'
    future = days < 0
    n, unit = _unit(abs(days))
    if unit == 'year' and n == 1:
        phrase = 'a year'
    else:
        phrase = f'{n} {unit}{"s" if n != 1 else ""}'
    return f'in {phrase}' if future else f'{phrase} ago'


def span_text(days: int) -> str:
    """A duration ('3 weeks', '8 years') for facts about gaps between two dates."""
    days = abs(days)
    if days < 14:
        return f'{days} day{"s" if days != 1 else ""}'
    if days < 60:
        n = max(2, round(days / 7))
        return f'{n} weeks'
    if days < 730:
        n = max(2, round(days / 30.4))
        return f'{n} months'
    n = max(2, round(days / 365.25))
    return f'{n} years'
