import json
import re
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from api import db
from api.models.issue import Issue
from api.models.series import Series
from api.models.series_entities import Genre, Creator, Character, Publisher
from api.models.user import User
from tests.base_test_case import BaseTestCase


class TestSeriesUpdate(BaseTestCase):
    def _series_with_entities(self):
        user = db.session.query(User).filter_by(username='test').first()
        series = Series(title='S', user=user)
        series.genre = [Genre(title='Superhero', user=user)]
        series.creator = [Creator(title='Alan Moore', user=user)]
        series.character = [Character(title='Batman', user=user)]
        series.publisher = [Publisher(title='DC', user=user)]
        db.session.add(series)
        db.session.commit()
        return series

    def test_partial_update_keeps_entities(self):
        series = self._series_with_entities()

        rv = self.client.put(f'/api/series/{series.id}', data={'user_rating': '4'})
        self.assertEqual(rv.status_code, 200)

        db.session.expire_all()
        series = db.session.get(Series, series.id)
        self.assertEqual(series.user_rating, 4.0)
        self.assertEqual([g.title for g in series.genre], ['Superhero'])
        self.assertEqual([c.title for c in series.creator], ['Alan Moore'])
        self.assertEqual([c.title for c in series.character], ['Batman'])
        self.assertEqual([p.title for p in series.publisher], ['DC'])

    def test_sent_entity_lists_replace_existing(self):
        series = self._series_with_entities()

        rv = self.client.put(f'/api/series/{series.id}', data={
            'genre': json.dumps([]),
            'creator': json.dumps([{'value': 'Frank Miller'}]),
        })
        self.assertEqual(rv.status_code, 200)

        db.session.expire_all()
        series = db.session.get(Series, series.id)
        self.assertEqual(list(series.genre), [])
        self.assertEqual([c.title for c in series.creator], ['Frank Miller'])
        # keys that were not sent are untouched
        self.assertEqual([c.title for c in series.character], ['Batman'])
        self.assertEqual([p.title for p in series.publisher], ['DC'])


class TestCollectionSorts(BaseTestCase):
    """Three series shaped so every sort key puts them in a different, obvious order."""

    def setUp(self):
        super().setUp()
        user = db.session.query(User).filter_by(username='test').first()
        dc = Publisher(title='DC', user=user)
        marvel = Publisher(title='Marvel', user=user)
        self.a = Series(title='Animal Man', user=user, issue_count=10, owned_count=10, read_count=5,
                        user_rating=3.0, purchase_cost=50.0,
                        timestamp=datetime(2026, 1, 1), publisher=[marvel])
        self.b = Series(title='Batman', user=user, issue_count=20, owned_count=5, read_count=5,
                        user_rating=5.0, purchase_cost=10.0,
                        timestamp=datetime(2026, 1, 2), publisher=[dc])
        self.c = Series(title='Constantine', user=user, issue_count=4, owned_count=0, read_count=0,
                        timestamp=datetime(2026, 1, 3))
        db.session.add_all([self.a, self.b, self.c])
        db.session.flush()
        db.session.add_all([
            Issue(title='1', number=1, series=self.a, user=user, is_owned=1, is_read=1,
                  bought_date=datetime(2026, 1, 1), read_date=datetime(2026, 3, 1)),
            Issue(title='1', number=1, series=self.b, user=user, is_owned=1, is_read=1,
                  bought_date=datetime(2026, 2, 1), read_date=datetime(2026, 2, 1)),
        ])
        db.session.commit()

    def titles(self, **params):
        rv = self.client.get('/api/users/series', query_string=params)
        self.assertEqual(rv.status_code, 200)
        return [s['title'] for s in rv.json['data']]

    def test_default_is_newest_added_first(self):
        self.assertEqual(self.titles(), ['Constantine', 'Batman', 'Animal Man'])

    def test_progress_shares_and_gaps(self):
        self.assertEqual(self.titles(orderBy='collected', orderDir='desc'), ['Animal Man', 'Batman', 'Constantine'])
        self.assertEqual(self.titles(orderBy='read', orderDir='desc'), ['Batman', 'Animal Man', 'Constantine'])
        self.assertEqual(self.titles(orderBy='missing', orderDir='desc'), ['Batman', 'Constantine', 'Animal Man'])
        # Batman and Constantine tie on unread; the title breaks it.
        self.assertEqual(self.titles(orderBy='unread', orderDir='desc'), ['Animal Man', 'Batman', 'Constantine'])

    def test_empty_values_go_last_whatever_the_direction(self):
        self.assertEqual(self.titles(orderBy='user_rating', orderDir='desc'), ['Batman', 'Animal Man', 'Constantine'])
        self.assertEqual(self.titles(orderBy='user_rating', orderDir='asc'), ['Animal Man', 'Batman', 'Constantine'])
        self.assertEqual(self.titles(orderBy='publisher', orderDir='asc'), ['Batman', 'Animal Man', 'Constantine'])

    def test_last_bought_and_last_read_come_from_the_issues(self):
        self.assertEqual(self.titles(orderBy='last_bought', orderDir='desc'), ['Batman', 'Animal Man', 'Constantine'])
        self.assertEqual(self.titles(orderBy='last_read', orderDir='desc'), ['Animal Man', 'Batman', 'Constantine'])

    def test_counts_and_spend(self):
        self.assertEqual(self.titles(orderBy='issue_count', orderDir='asc'), ['Constantine', 'Animal Man', 'Batman'])
        self.assertEqual(self.titles(orderBy='purchase_cost', orderDir='desc'), ['Animal Man', 'Batman', 'Constantine'])

    def test_list_rows_leave_out_the_heavy_fields(self):
        rv = self.client.get('/api/users/series')
        row = rv.json['data'][0]
        for key in ('character', 'creator', 'description', 'notes', 'user'):
            self.assertNotIn(key, row)
        for key in ('publisher', 'genre', 'thumbnail', 'owned_count', 'dominant_color', 'series_format'):
            self.assertIn(key, row)
        rv = self.client.get(f"/api/series/{self.b.id}")
        self.assertEqual(rv.status_code, 200)
        self.assertIn('character', rv.json)

    def test_filter_values_come_in_one_response(self):
        rv = self.client.get('/api/series/filters')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(set(rv.json), {'publisher', 'creator', 'character', 'genre', 'series_format'})
        publishers = sorted({p.title for p in db.session.scalars(Publisher.select()).all()})
        self.assertEqual([o['value'] for o in rv.json['publisher']], publishers)
        self.assertEqual(rv.json['publisher'][0]['id'], '1')
        self.assertEqual(rv.json['series_format'], [])

    def test_list_page_loads_publishers_and_genres_once_each(self):
        hits = []
        listener = lambda conn, cursor, statement, *args: hits.append(statement)
        event.listen(Engine, 'before_cursor_execute', listener)
        try:
            rv = self.client.get('/api/users/series')
        finally:
            event.remove(Engine, 'before_cursor_execute', listener)
        self.assertEqual(len(rv.json['data']), 3)
        self.assertEqual(sum(bool(re.search(r'FROM .*\bpublisher\b', s)) for s in hits), 1)
        self.assertEqual(sum(bool(re.search(r'FROM .*\bgenre\b', s)) for s in hits), 1)

    def test_unknown_sort_is_refused(self):
        rv = self.client.get('/api/users/series', query_string={'orderBy': 'user'})
        self.assertEqual(rv.status_code, 400)


class SeriesEntityWriteTests(BaseTestCase):
    def test_create_dedupes_and_update_replaces(self):
        rv = self.client.post('/api/series', data={
            'title': 'Hellblazer', 'issue_count': '3',
            'publisher': json.dumps(['DC Comics', 'DC Comics']),
            'genre': json.dumps([{'value': 'Horror'}, {'value': 'Occult'}]),
        })
        self.assertEqual(rv.status_code, 201, rv.json)
        series = db.session.get(Series, rv.json['id'])
        self.assertEqual([p.title for p in series.publisher], ['DC Comics'])
        self.assertEqual(sorted(g.title for g in series.genre), ['Horror', 'Occult'])

        rv = self.client.put(f'/api/series/{series.id}', data={'publisher': json.dumps(['Vertigo']), 'genre': json.dumps([])})
        self.assertEqual(rv.status_code, 200, rv.json)
        db.session.refresh(series)
        self.assertEqual([p.title for p in series.publisher], ['Vertigo'])
        self.assertEqual(list(series.genre), [])
        self.assertEqual(sorted(p.title for p in db.session.scalars(Publisher.select())), ['DC Comics', 'Vertigo'])
