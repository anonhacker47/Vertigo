from datetime import datetime, timezone

from api import db
from api.models.issue import Issue
from api.models.series import Series
from api.models.user import User
from tests.base_test_case import BaseTestCase


class TestPurchasesPerMonth(BaseTestCase):
    def test_counts_and_spend_per_month(self):
        user = db.session.scalar(User.select().where(User.username == 'test'))
        series = Series(title='Watchmen', user=user)
        db.session.add(series)
        db.session.flush()

        db.session.add_all([
            Issue(title='#1', number=1, series=series,
                  bought_date=datetime(2026, 3, 5, tzinfo=timezone.utc), bought_price=4.99),
            Issue(title='#2', number=2, series=series,
                  bought_date=datetime(2026, 3, 20, tzinfo=timezone.utc), bought_price=5.01),
            Issue(title='#3', number=3, series=series,
                  bought_date=datetime(2026, 4, 1, tzinfo=timezone.utc), bought_price=None),
            Issue(title='#4', number=4, series=series,
                  bought_date=datetime(2025, 12, 1, tzinfo=timezone.utc), bought_price=99),
        ])
        db.session.commit()

        rv = self.client.get('/api/users/purchases_per_month?year=2026')

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json, [
            {'month': '2026-03', 'count': 2, 'spent': 10.0},
            {'month': '2026-04', 'count': 1, 'spent': 0},
        ])
