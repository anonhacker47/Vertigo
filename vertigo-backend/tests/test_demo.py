from api import db
from api.demo import MESSAGE
from api.models.series import Series
from api.models.series_entities import Publisher
from api.models.user import User
from tests.base_test_case import BaseTestCase, TestConfig, TestConfigWithAuth


class DemoConfig(TestConfig):
    DEMO_MODE = True


class DemoWithAuthConfig(TestConfigWithAuth):
    DEMO_MODE = True


class DemoModeTests(BaseTestCase):
    config = DemoConfig

    def setUp(self):
        super().setUp()
        user = db.session.scalar(User.select().where(User.username == 'test'))
        self.series = Series(title='A', user=user)
        db.session.add(self.series)
        db.session.commit()

    def refused(self, rv):
        self.assertEqual(rv.status_code, 403)
        self.assertEqual(rv.json['description'], MESSAGE)

    def test_writes_are_refused(self):
        url = f'/api/series/{self.series.id}'
        self.refused(self.client.post('/api/series', data={'title': 'B'}))
        self.refused(self.client.put(url, data={'title': 'B'}))
        self.refused(self.client.delete(url))
        self.refused(self.client.put('/api/me', data={'username': 'x'}))
        self.refused(self.client.post('/api/users', json={
            'username': 'new', 'email': 'new@example.com', 'password': 'foo'}))
        self.refused(self.client.post('/api/restore'))
        self.refused(self.client.delete('/api/delete_all_data'))
        self.assertIsNotNone(db.session.get(Series, self.series.id))

    def test_reads_and_downloads_work(self):
        self.assertEqual(self.client.get(f'/api/series/{self.series.id}').status_code, 200)
        for url in ('/api/backup', '/api/export_data'):
            rv = self.client.get(url)
            self.assertEqual(rv.status_code, 200)
            rv.close()

    def test_external_lookups_are_refused(self):
        self.refused(self.client.get('/api/metron/series/search?name=x'))
        self.refused(self.client.get('/api/tenrai/manga/search?q=x'))

    def test_ping_reports_demo(self):
        self.assertIs(self.client.get('/api/ping').json['demo'], True)


class DemoSignInTests(BaseTestCase):
    config = DemoWithAuthConfig

    def test_login_refresh_and_logout_work(self):
        rv = self.client.post('/api/tokens', auth=('test', 'foo'))
        self.assertEqual(rv.status_code, 200)
        access, refresh = rv.json['access_token'], rv.json['refresh_token']
        rv = self.client.put('/api/tokens', json={
            'access_token': access, 'refresh_token': refresh})
        self.assertEqual(rv.status_code, 200)
        rv = self.client.delete('/api/tokens', headers={
            'Authorization': f"Bearer {rv.json['access_token']}"})
        self.assertEqual(rv.status_code, 204)


class NormalModeTests(BaseTestCase):
    def test_ping_reports_no_demo(self):
        self.assertIs(self.client.get('/api/ping').json['demo'], False)

    def test_writes_work(self):
        rv = self.client.post('/api/series', data={'title': 'B'})
        self.assertLess(rv.status_code, 300)

    def test_full_sync_is_scoped_to_the_user(self):
        me = db.session.scalar(User.select().where(User.username == 'test'))
        other = User(username='other', email='other@example.com', password='foo')
        db.session.add_all([other, Publisher(title='Mine', user=me),
                            Publisher(title='Theirs', user=other)])
        db.session.commit()
        titles = [p['title'] for p in self.client.get('/api/sync/full').json['publishers']]
        self.assertEqual(titles, ['Mine'])
