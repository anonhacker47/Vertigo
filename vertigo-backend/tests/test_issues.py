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
