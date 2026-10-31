from api import db
from api.models.issue import Issue
from api.models.series import Series
from api.models.series_entities import Character, Creator, Publisher
from api.models.user import User
from tests.base_test_case import BaseTestCase


class TestSearch(BaseTestCase):
    """Two Batman series and a Superman one, with a few issues and entities; a second user's shelf must stay hidden."""

    def setUp(self):
        super().setUp()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))
        other = User(username='other', email='other@example.com', password='foo')
        db.session.add(other)

        batman = Series(title='Batman', user=self.user, issue_count=2, owned_count=1, thumbnail='x.jpg')
        beyond = Series(title='Batman Beyond', user=self.user, issue_count=0, owned_count=0)
        superman = Series(title='Superman', user=self.user, issue_count=1, owned_count=0)
        hidden = Series(title='Batgirl', user=other)
        db.session.add_all([batman, beyond, superman, hidden])
        db.session.flush()
        db.session.add_all([
            Issue(title='Year One', number=1, series=batman, user=self.user, is_owned=1, is_read=0),
            Issue(title='12', number=12, series=batman, user=self.user, is_owned=0, is_read=0),
            Issue(title='12', number=12, series=superman, user=self.user, is_owned=0, is_read=0),
            Issue(title='Year One', number=1, series=hidden, user=other, is_owned=0, is_read=0),
            Publisher(title='DC Comics', user=self.user, thumbnail='dc.jpg'),
            Publisher(title='Dark Horse', user=other),
            Creator(title='Frank Miller', user=self.user),
            Character(title='Batman', user=self.user),
        ])
        db.session.commit()

    def search(self, q, **params):
        rv = self.client.get('/api/search', query_string={'q': q, **params})
        self.assertEqual(rv.status_code, 200)
        return rv.json

    def test_matches_every_group_for_the_current_user_only(self):
        body = self.search('bat')
        self.assertEqual([s['title'] for s in body['series']], ['Batman', 'Batman Beyond'])
        self.assertEqual([c['title'] for c in body['characters']], ['Batman'])
        self.assertEqual(body['issues'], [])
        self.assertEqual(body['publishers'], [])
        self.assertEqual(body['creators'], [])

    def test_custom_issue_titles_match_but_default_number_titles_do_not(self):
        body = self.search('year')
        self.assertEqual([(i['series']['title'], i['number']) for i in body['issues']], [('Batman', 1)])
        self.assertEqual(self.search('12')['issues'][0]['series']['title'], 'Batman')
        self.assertEqual(len(self.search('12')['issues']), 2)

    def test_series_name_plus_number_narrows_to_that_issue(self):
        body = self.search('batman #12')
        self.assertEqual([(i['series']['title'], i['number']) for i in body['issues']], [('Batman', 12)])
        self.assertEqual(body['series'], [])

    def test_thumbnails_are_urls_only_when_set(self):
        body = self.search('bat')
        by_title = {s['title']: s for s in body['series']}
        self.assertIn('/series/image/', by_title['Batman']['thumbnail'])
        self.assertIsNone(by_title['Batman Beyond']['thumbnail'])
        self.assertIn('/publisher/image/', self.search('dc')['publishers'][0]['thumbnail'])

    def test_short_or_empty_query_returns_nothing(self):
        for q in ('', ' ', 'b'):
            body = self.search(q)
            self.assertEqual(sum(len(body[k]) for k in ('series', 'issues', 'publishers', 'creators', 'characters')), 0)

    def test_limit_caps_each_group(self):
        self.assertEqual(len(self.search('bat', limit=1)['series']), 1)
        self.assertEqual(len(self.search('bat', limit=0)['series']), 1)
        self.assertEqual(len(self.search('bat', limit='x')['series']), 2)
