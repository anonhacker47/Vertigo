from api import db
from api.models.issue import Issue
from api.models.series import Series
from api.models.series_entities import Character, Creator, Publisher
from api.models.user import User
from tests.base_test_case import BaseTestCase


class TestOwnerChecks(BaseTestCase):
    """The caller is 'test'; everything below belongs to someone else."""

    def setUp(self):
        super().setUp()
        self.other = User(username='other', email='other@example.com', password='bar')
        self.series = Series(title='Saga', user=self.other, issue_count=1)
        db.session.add_all([self.other, self.series])
        db.session.flush()
        self.entities = {
            'publisher': Publisher(title='Image', user=self.other),
            'creator': Creator(title='Fiona Staples', user=self.other),
            'character': Character(title='Alana', user=self.other),
        }
        db.session.add_all([Issue(title='1', number=1, series=self.series, user=self.other, is_owned=1, is_read=0),
                            *self.entities.values()])
        db.session.commit()

    def test_someone_elses_series_cannot_be_read(self):
        sid = self.series.id
        for url in (f'/api/series/{sid}', f'/api/series/{sid}/issues', f'/api/series/{sid}/issue_count',
                    f'/api/series/{sid}/issues/1/', f'/api/series/{sid}/neighbors'):
            self.assertEqual(self.client.get(url).status_code, 403, url)

    def test_issues_cannot_be_added_to_someone_elses_series(self):
        rv = self.client.post(f'/api/series/{self.series.id}/issues',
                              json=[{'title': '2', 'number': 2, 'is_owned': True, 'is_read': False}])
        self.assertEqual(rv.status_code, 403)
        self.assertEqual(len(db.session.scalars(Issue.select()).all()), 1)

    def test_someone_elses_entities_cannot_be_read_or_edited(self):
        for name, entity in self.entities.items():
            url = f'/api/{name}/{entity.id}'
            self.assertEqual(self.client.get(url).status_code, 403, url)
            self.assertEqual(self.client.get(f'{url}/neighbours').status_code, 403, url)
            for method in (self.client.put, self.client.patch):
                self.assertEqual(method(url, data={'title': 'Mine now'}).status_code, 403, url)
            db.session.refresh(entity)
            self.assertNotEqual(entity.title, 'Mine now')

    def test_only_your_own_user_record_is_served(self):
        me = db.session.scalar(User.select().filter_by(username='test'))
        self.assertEqual(self.client.get(f'/api/users/{me.id}').status_code, 200)
        self.assertEqual(self.client.get(f'/api/users/{self.other.id}').status_code, 404)

    def test_cross_user_listings_are_gone(self):
        for url in ('/api/series', '/api/series/issues/', '/api/series/key'):
            self.assertIn(self.client.get(url).status_code, (404, 405), url)

    def test_missing_rows_are_still_404(self):
        self.assertEqual(self.client.get('/api/series/999').status_code, 404)
        self.assertEqual(self.client.get('/api/publisher/999').status_code, 404)
