"""Load a user's shelf once and derive the per-series facts every insight is built on.

    candidate    owned and unread - the reading queue is made of these
    missing      an issue row that is not owned
    run          a series with two or more issues; single volumes are one-shots
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from api import db
from sqlalchemy import select
from api.models.issue import Issue
from api.models.series import Series
from api.models import associations
from api.models.series_entities import Creator, Publisher


def utcnow() -> datetime:
    """Naive UTC 'now', matching how the models store their datetimes."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def as_naive(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalise a possibly tz-aware datetime to naive UTC."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def days_between(later: Optional[datetime], earlier: Optional[datetime]) -> Optional[int]:
    if later is None or earlier is None:
        return None
    return (as_naive(later).date() - as_naive(earlier).date()).days


@dataclass
class SeriesFacts:
    series: Series
    issues: list = field(default_factory=list)  # sorted by number
    publisher: Optional[Publisher] = None
    creators: list = field(default_factory=list)

    # ------------------------------------------------------------------ counts
    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def is_run(self) -> bool:
        return self.issue_count >= 2

    @property
    def owned(self) -> list:
        return [i for i in self.issues if i.is_owned]

    @property
    def missing(self) -> list:
        return [i for i in self.issues if not i.is_owned]

    @property
    def read(self) -> list:
        return [i for i in self.issues if i.is_read]

    def candidates(self) -> list:
        return [i for i in self.owned if not i.is_read]

    # --------------------------------------------------------------- positions
    @property
    def last_read_number(self) -> Optional[int]:
        read = self.read
        return max(i.number for i in read) if read else None

    @property
    def last_read_at(self) -> Optional[datetime]:
        dates = [as_naive(i.read_date) for i in self.issues if i.is_read and i.read_date]
        return max(dates) if dates else None

    @property
    def next_number_after_last_read(self) -> Optional[int]:
        """Lowest issue number above the highest read one (owned or not)."""
        last = self.last_read_number
        if last is None:
            return None
        later = [i.number for i in self.issues if i.number > last]
        return min(later) if later else None

    @property
    def first_number(self) -> Optional[int]:
        return self.issues[0].number if self.issues else None

    def issue_by_number(self, number: Optional[int]) -> Optional[Issue]:
        if number is None:
            return None
        for i in self.issues:
            if i.number == number:
                return i
        return None

    def last_bought_at(self) -> Optional[datetime]:
        dates = [as_naive(i.bought_date) for i in self.owned if i.bought_date]
        if dates:
            return max(dates)
        return as_naive(self.series.timestamp)

    @property
    def fully_collected(self) -> bool:
        return self.issue_count > 0 and len(self.owned) == self.issue_count

    @property
    def fully_read(self) -> bool:
        return self.issue_count > 0 and len(self.read) == self.issue_count

    @property
    def is_manga(self) -> bool:
        return bool(self.series.manga) or (self.series.series_format or '').strip().lower() == 'manga'


@dataclass
class Collection:
    user_id: int
    now: datetime
    series: list  # list[SeriesFacts]

    @property
    def all_issues(self) -> list:
        return [i for s in self.series for i in s.issues]

    def owned(self) -> list:
        return [i for s in self.series for i in s.owned]

    def candidates(self) -> list:
        return [i for s in self.series for i in s.candidates()]

    def by_series_id(self, series_id: int) -> Optional[SeriesFacts]:
        for s in self.series:
            if s.series.id == series_id:
                return s
        return None

    def facts_for_issue(self, issue: Issue) -> Optional[SeriesFacts]:
        return self.by_series_id(issue.series_id)

    def duplicate_titles(self) -> set:
        seen, dupes = set(), set()
        for s in self.series:
            key = (s.series.title or '').strip().lower()
            if key in seen:
                dupes.add(key)
            seen.add(key)
        return dupes


def load_collection(user_id: int, now: Optional[datetime] = None) -> Collection:
    """Two queries for the shelf plus two light joins for publisher and creators."""
    now = now or utcnow()

    series_rows = db.session.scalars(
        Series.select().where(Series.user_id == user_id).order_by(Series.title)
    ).all()
    issue_rows = db.session.scalars(
        Issue.select().where(Issue.user_id == user_id).order_by(Issue.series_id, Issue.number)
    ).all()

    facts = {s.id: SeriesFacts(series=s) for s in series_rows}
    for issue in issue_rows:
        if issue.series_id in facts:
            facts[issue.series_id].issues.append(issue)

    if facts:
        ids = list(facts.keys())
        pub_rows = db.session.execute(
            select(associations.series_publisher.c.series_id, Publisher)
            .join(Publisher, Publisher.id == associations.series_publisher.c.publisher_id)
            .where(associations.series_publisher.c.series_id.in_(ids))
        ).all()
        for series_id, publisher in pub_rows:
            if facts[series_id].publisher is None:
                facts[series_id].publisher = publisher

        creator_rows = db.session.execute(
            select(associations.series_creator.c.series_id, Creator)
            .join(Creator, Creator.id == associations.series_creator.c.creator_id)
            .where(associations.series_creator.c.series_id.in_(ids))
        ).all()
        for series_id, creator in creator_rows:
            facts[series_id].creators.append(creator)

    return Collection(user_id=user_id, now=now, series=list(facts.values()))
