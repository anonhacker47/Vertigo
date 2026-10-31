from api import db
from api.models.issue import Issue
from api.models.series import Series
from api.models.user import User
from tests.base_test_case import BaseTestCase


class IssueTestCase(BaseTestCase):
    """A three-issue series: #1 owned for 4.0, #2 and #3 not owned."""

    def setUp(self):
        super().setUp()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))
        self.series = Series(title='Hellblazer', user=self.user, issue_count=3, owned_count=1, read_count=0)
        db.session.add(self.series)
        db.session.flush()
        for n in (1, 2, 3):
            db.session.add(Issue(
                title=str(n), number=n, series=self.series, user=self.user,
                is_owned=1 if n == 1 else 0, is_read=0, bought_price=4.0 if n == 1 else None,
            ))
        db.session.commit()

    def create_url(self):
        return f'/api/series/{self.series.id}/single_issue'

    def issue(self, number):
        return db.session.scalar(Issue.select().where(Issue.series_id == self.series.id, Issue.number == number))

    def numbers(self):
        return sorted(i.number for i in db.session.scalars(self.series.issue_select()))


class TestCreateSingleIssue(IssueTestCase):
    def test_creates_with_number_title_and_status(self):
        rv = self.client.post(self.create_url(), json={
            'number': 5, 'title': 'Dangerous Habits', 'is_owned': True, 'bought_price': 3.5,
        })
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(rv.json['number'], 5)
        self.assertEqual(rv.json['title'], 'Dangerous Habits')
        self.assertTrue(rv.json['is_owned'])
        self.assertIsNotNone(rv.json['bought_date'])  # stamped because nothing was given

        db.session.refresh(self.series)
        self.assertEqual(self.series.issue_count, 4)
        self.assertEqual(self.series.owned_count, 2)
        self.assertEqual(self.series.purchase_cost, 7.5)

    def test_requires_a_number(self):
        rv = self.client.post(self.create_url(), json={'title': 'Untitled'})
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(self.numbers(), [1, 2, 3])

    def test_title_defaults_to_the_number(self):
        rv = self.client.post(self.create_url(), json={'number': 4})
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(rv.json['title'], '4')

    def test_fills_a_gap_but_rejects_a_duplicate(self):
        rv = self.client.delete(f'/api/series/issues/{self.issue(2).id}/')
        self.assertEqual(rv.status_code, 204)

        rv = self.client.post(self.create_url(), json={'number': 2})
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(self.numbers(), [1, 2, 3])

        rv = self.client.post(self.create_url(), json={'number': 2})
        self.assertEqual(rv.status_code, 409)
        self.assertIn('#2', rv.json['description'])
        self.assertEqual(self.numbers(), [1, 2, 3])

    def test_rejects_a_negative_number(self):
        rv = self.client.post(self.create_url(), json={'number': -1})
        self.assertEqual(rv.status_code, 400)


class TestDeleteIssue(IssueTestCase):
    def test_deletes_any_issue_and_recounts(self):
        rv = self.client.delete(f'/api/series/issues/{self.issue(1).id}/')
        self.assertEqual(rv.status_code, 204)
        self.assertEqual(self.numbers(), [2, 3])

        db.session.refresh(self.series)
        self.assertEqual(self.series.issue_count, 2)
        self.assertEqual(self.series.owned_count, 0)
        self.assertEqual(self.series.purchase_cost, 0)


class TestListIssues(IssueTestCase):
    def test_orders_by_number_numerically(self):
        for n in range(4, 13):
            db.session.add(Issue(title=str(n), number=n, series=self.series, user=self.user, is_owned=0, is_read=0))
        db.session.commit()

        rv = self.client.get(f'/api/series/{self.series.id}/issues?orderBy=number&orderDir=asc')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual([i['number'] for i in rv.json['data']], list(range(1, 13)))

        rv = self.client.get(f'/api/series/{self.series.id}/issues?orderBy=number&orderDir=desc')
        self.assertEqual([i['number'] for i in rv.json['data']], list(range(12, 0, -1)))


class TestListUserIssues(IssueTestCase):
    """GET /users/issues: every issue the user owns, across series, with a series reference."""

    def setUp(self):
        super().setUp()
        self.other_series = Series(title='Sandman', user=self.user, issue_count=1, owned_count=0, read_count=0)
        db.session.add(self.other_series)
        db.session.flush()
        db.session.add(Issue(title='Sleep of the Just', number=1, series=self.other_series,
                             user=self.user, is_owned=0, is_read=0, user_rating=4.5))

        stranger = User(username='stranger', email='stranger@example.com', password='foo')
        db.session.add(stranger)
        db.session.flush()
        their_series = Series(title='Preacher', user=stranger, issue_count=1, owned_count=0, read_count=0)
        db.session.add(their_series)
        db.session.flush()
        db.session.add(Issue(title='1', number=1, series=their_series, user=stranger, is_owned=0, is_read=0))
        db.session.commit()

    def test_lists_only_the_users_issues_with_a_series_reference(self):
        rv = self.client.get('/api/users/issues')
        self.assertEqual(rv.status_code, 200)
        rows = rv.json['data']
        self.assertEqual(len(rows), 4)
        self.assertEqual(rv.json['pagination']['total'], 4)
        self.assertTrue(all(r['user_id'] == self.user.id for r in rows))
        self.assertNotIn('Preacher', {r['series']['title'] for r in rows})

        sandman = next(r for r in rows if r['series']['title'] == 'Sandman')
        self.assertEqual(sandman['number'], 1)
        self.assertEqual(sandman['title'], 'Sleep of the Just')
        self.assertEqual(sandman['user_rating'], 4.5)
        self.assertEqual(sandman['series_id'], self.other_series.id)
        self.assertEqual(set(sandman['series']), {'id', 'title', 'slug', 'manga', 'thumbnail', 'last_updated'})
        self.assertEqual(sandman['series']['slug'], 'sandman')

    def test_pages_in_id_order(self):
        rv = self.client.get('/api/users/issues?limit=3&offset=0')
        self.assertEqual(rv.status_code, 200)
        first = [r['id'] for r in rv.json['data']]
        self.assertEqual(len(first), 3)
        self.assertEqual(first, sorted(first))

        rv = self.client.get('/api/users/issues?limit=3&offset=3')
        self.assertEqual(rv.status_code, 200)
        rest = [r['id'] for r in rv.json['data']]
        self.assertEqual(len(rest), 1)
        self.assertGreater(rest[0], first[-1])


class TestBulkIssues(IssueTestCase):
    def bulk_url(self):
        return f'/api/series/{self.series.id}/issues/bulk'

    def ids(self, *numbers):
        return [self.issue(n).id for n in numbers]

    def test_marks_several_owned_with_one_date_and_price(self):
        rv = self.client.put(self.bulk_url(), json={
            'ids': self.ids(2, 3), 'is_owned': True,
            'bought_date': '2026-10-01T00:00:00Z', 'bought_price': 2.5,
        })
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(sorted(i['number'] for i in rv.json), [2, 3])
        for n in (2, 3):
            issue = self.issue(n)
            self.assertTrue(issue.is_owned)
            self.assertEqual(issue.bought_price, 2.5)
            self.assertEqual(issue.bought_date.strftime('%Y-%m-%d'), '2026-10-01')
        db.session.refresh(self.series)
        self.assertEqual(self.series.owned_count, 3)
        self.assertEqual(self.series.purchase_cost, 9.0)

    def test_clearing_owned_drops_date_and_price(self):
        rv = self.client.put(self.bulk_url(), json={'ids': self.ids(1), 'is_owned': False})
        self.assertEqual(rv.status_code, 200)
        issue = self.issue(1)
        self.assertFalse(issue.is_owned)
        self.assertIsNone(issue.bought_date)
        self.assertIsNone(issue.bought_price)
        db.session.refresh(self.series)
        self.assertEqual(self.series.owned_count, 0)
        self.assertEqual(self.series.purchase_cost, 0)

    def test_marking_read_without_a_date_stamps_now(self):
        rv = self.client.put(self.bulk_url(), json={'ids': self.ids(1, 2), 'is_read': True})
        self.assertEqual(rv.status_code, 200)
        for n in (1, 2):
            self.assertTrue(self.issue(n).is_read)
            self.assertIsNotNone(self.issue(n).read_date)
        self.assertFalse(self.issue(3).is_read)
        db.session.refresh(self.series)
        self.assertEqual(self.series.read_count, 2)

    def test_rejects_an_issue_from_another_series_and_changes_nothing(self):
        other = Series(title='Swamp Thing', user=self.user)
        db.session.add(other)
        db.session.flush()
        stray = Issue(title='1', number=1, series=other, user=self.user, is_owned=0, is_read=0)
        db.session.add(stray)
        db.session.commit()

        rv = self.client.put(self.bulk_url(), json={'ids': self.ids(2) + [stray.id], 'is_owned': True})
        self.assertEqual(rv.status_code, 404)
        self.assertFalse(self.issue(2).is_owned)
        self.assertFalse(db.session.get(Issue, stray.id).is_owned)

    def test_requires_at_least_one_id(self):
        rv = self.client.put(self.bulk_url(), json={'ids': [], 'is_owned': True})
        self.assertEqual(rv.status_code, 400)

    def test_deletes_several_and_recounts(self):
        rv = self.client.delete(self.bulk_url(), json={'ids': self.ids(2, 3)})
        self.assertEqual(rv.status_code, 204)
        self.assertEqual(self.numbers(), [1])
        db.session.refresh(self.series)
        self.assertEqual(self.series.issue_count, 1)
        self.assertEqual(self.series.owned_count, 1)
