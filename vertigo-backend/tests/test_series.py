import json
from api import db
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
