import time

from api import db
from api.models.issue import Issue
from api.models.series import Series
from api.models.series_entities import Publisher
from api.models.user import User
from tests.base_test_case import BaseTestCase


class ThumbnailUpdatedTests(BaseTestCase):
    """``thumbnail_updated`` follows the image, not the row."""

    def setUp(self):
        super().setUp()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))

    def test_set_on_create_only_when_there_is_an_image(self):
        with_cover = Series(title='A', user=self.user, thumbnail='series/1/cover.jpeg')
        without = Series(title='B', user=self.user)
        db.session.add_all([with_cover, without])
        db.session.commit()
        self.assertIsNotNone(with_cover.thumbnail_updated)
        self.assertIsNone(without.thumbnail_updated)

    def test_ordinary_edits_leave_it_alone(self):
        series = Series(title='A', user=self.user, thumbnail='series/1/cover.jpeg')
        db.session.add(series)
        db.session.commit()
        stamp = series.thumbnail_updated
        time.sleep(0.05)
        series.description = 'edited'
        series.user_rating = 4.5
        db.session.commit()
        self.assertEqual(series.thumbnail_updated, stamp)
        self.assertGreater(series.last_updated, stamp)

    def test_moves_when_the_path_changes_or_the_file_is_replaced(self):
        issue = Issue(title='1', number=1, user=self.user, thumbnail='series/1/issues/1.jpeg')
        db.session.add(issue)
        db.session.commit()
        first = issue.thumbnail_updated
        time.sleep(0.05)
        issue.thumbnail = 'series/1/issues/1.png'
        db.session.commit()
        second = issue.thumbnail_updated
        self.assertGreater(second, first)
        time.sleep(0.05)
        issue.touch_thumbnail()  # same path, new bytes
        db.session.commit()
        self.assertGreater(issue.thumbnail_updated, second)

    def test_clearing_the_image_moves_it_too(self):
        publisher = Publisher(title='DC', user=self.user, thumbnail='entities/publisher/1.jpeg')
        db.session.add(publisher)
        db.session.commit()
        first = publisher.thumbnail_updated
        time.sleep(0.05)
        publisher.thumbnail = None
        db.session.commit()
        self.assertGreater(publisher.thumbnail_updated, first)

    def test_sync_and_entity_payloads_carry_it(self):
        series = Series(title='A', user=self.user, thumbnail='series/1/cover.jpeg')
        db.session.add(series)
        db.session.flush()
        db.session.add(Issue(title='1', number=1, series=series, user=self.user, thumbnail='series/1/issues/1.jpeg'))
        db.session.add(Publisher(title='DC', user=self.user, thumbnail='entities/publisher/1.jpeg'))
        db.session.commit()

        data = self.client.get('/api/sync').get_json()
        self.assertTrue(data['series'][0]['thumbnail_updated'])
        self.assertTrue(data['issues'][0]['thumbnail_updated'])
        publishers = self.client.get('/api/publisher').get_json()
        self.assertTrue(publishers['data'][0]['thumbnail_updated'])
