from datetime import datetime, timedelta, timezone

from api import db
from api.models.issue import Issue
from api.models.series import Series
from api.models.user import User
from tests.base_test_case import BaseTestCase


def ago(days):
    return datetime.now(timezone.utc) - timedelta(days=days)


def last_year_today():
    now = datetime.now(timezone.utc)
    try:
        return now.replace(year=now.year - 1)
    except ValueError:  # 29 Feb
        return now.replace(year=now.year - 1, day=28)


def this_year(month, day=1):
    return datetime.now(timezone.utc).replace(month=month, day=day, hour=12, minute=0, second=0, microsecond=0)


class InsightsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))

    def add_series(self, title, issues, **kwargs):
        """issues: list of dicts with number and optional owned/read/bought/read_at/price."""
        series = Series(title=title, user=self.user, issue_count=len(issues), **kwargs)
        db.session.add(series)
        db.session.flush()
        for spec in issues:
            db.session.add(Issue(
                title=str(spec['number']), number=spec['number'], series=series, user=self.user,
                is_owned=1 if spec.get('owned') else 0,
                is_read=1 if spec.get('read') else 0,
                bought_date=spec.get('bought'),
                read_date=spec.get('read_at'),
                bought_price=spec.get('price'),
            ))
        series.owned_count = sum(1 for s in issues if s.get('owned'))
        series.read_count = sum(1 for s in issues if s.get('read'))
        db.session.commit()
        return series


class TestEmptyShelf(InsightsTestCase):
    def test_every_endpoint_returns_empty_shapes(self):
        rv = self.client.get('/api/insights/up-next')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['state'], 'no_series')
        self.assertIsNone(rv.json['hero'])

        rv = self.client.get('/api/insights/reading-queue')
        self.assertEqual(rv.json['total_unread'], 0)
        self.assertEqual(rv.json['items'], [])

        rv = self.client.get('/api/insights/get-next')
        self.assertEqual(rv.json['items'], [])
        self.assertEqual(rv.json['one_away'], 0)

        rv = self.client.get('/api/insights/activity')
        self.assertEqual(len(rv.json['buckets']), datetime.now().month)
        self.assertEqual(rv.json['totals'], {'bought': 0, 'read': 0})
        self.assertIsNone(rv.json['figures']['last_read'])

        rv = self.client.get('/api/insights/records')
        self.assertEqual(rv.json['completed'], [])
        self.assertIsNone(rv.json['firsts']['first_read'])

        rv = self.client.get('/api/insights/facts')
        self.assertIsNone(rv.json['on_this_day'])
        self.assertEqual(rv.json['facts'], [])


class TestUpNext(InsightsTestCase):
    def test_recent_continuation_beats_fresh_start_beats_stalled(self):
        self.add_series('Akira', [
            {'number': 1, 'owned': True, 'read': True, 'bought': ago(120), 'read_at': ago(20)},
            {'number': 2, 'owned': True, 'bought': ago(120)},
            {'number': 3, 'owned': False},
        ], dominant_color='(17, 89, 204)')
        self.add_series('The Demon', [{'number': 1, 'owned': True, 'bought': ago(5)}])
        self.add_series('The Mask', [
            {'number': 1, 'owned': True, 'read': True, 'bought': ago(800), 'read_at': ago(700)},
            {'number': 2, 'owned': True, 'bought': ago(400)},
        ])

        rv = self.client.get('/api/insights/up-next')
        self.assertEqual(rv.status_code, 200)
        hero = rv.json['hero']
        self.assertEqual(rv.json['state'], 'ok')
        self.assertEqual(hero['series']['title'], 'Akira')
        self.assertEqual(hero['issue']['number'], 2)
        self.assertEqual(hero['tier'], '1a')
        self.assertEqual(hero['reason'], 'You read Akira #1, 3 weeks ago. #2 is on the shelf.')
        self.assertEqual(hero['label'], 'Akira #2')
        self.assertEqual(hero['series']['dominant_color'], '#1159cc')
        self.assertIsNone(rv.json['on_deck'][0]['series']['dominant_color'])
        self.assertEqual([d['label'] for d in rv.json['on_deck']], ['The Demon', 'The Mask #2'])
        self.assertEqual([d['tier'] for d in rv.json['on_deck']], ['2a', '1b'])
        self.assertTrue(rv.json['on_deck'][1]['label'].endswith('#2'))

    def test_nothing_owned_and_nothing_unread_states(self):
        self.add_series('Watchmen', [{'number': 1, 'owned': False}])
        rv = self.client.get('/api/insights/up-next')
        self.assertEqual(rv.json['state'], 'nothing_owned')

        self.add_series('We3', [{'number': 1, 'owned': True, 'read': True, 'read_at': ago(3)}])
        rv = self.client.get('/api/insights/up-next')
        self.assertEqual(rv.json['state'], 'nothing_unread')


class TestReadingQueue(InsightsTestCase):
    def test_excludes_hero_and_marks_rows(self):
        self.add_series('Akira', [
            {'number': 1, 'owned': True, 'read': True, 'read_at': ago(20)},
            {'number': 2, 'owned': True},
        ])
        self.add_series('Monster', [{'number': 1, 'owned': True, 'bought': ago(10)},
                                    {'number': 2, 'owned': True, 'bought': ago(10)}])
        self.add_series('Doom Patrol', [
            {'number': 1, 'owned': True, 'read': True, 'read_at': ago(400)},
            {'number': 2, 'owned': True, 'bought': ago(300)},
            {'number': 3, 'owned': True, 'bought': ago(300)},
        ])
        self.add_series('Hitman', [{'number': 1, 'owned': True, 'bought': ago(900)},
                                   {'number': 2, 'owned': False}])

        rv = self.client.get('/api/insights/reading-queue')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['total_unread'], 6)   # Akira 1 + Monster 2 + Doom Patrol 2 + Hitman 1
        self.assertEqual(rv.json['series_count'], 4)
        titles = [row['series']['title'] for row in rv.json['items']]
        self.assertNotIn('Akira', titles)
        self.assertEqual(titles, ['Monster', 'Doom Patrol', 'Hitman'])
        markers = {row['series']['title']: row['marker'] for row in rv.json['items']}
        self.assertEqual(markers, {'Monster': 'fresh', 'Doom Patrol': 'stalled', 'Hitman': 'not_started'})
        doom = next(r for r in rv.json['items'] if r['series']['title'] == 'Doom Patrol')
        self.assertEqual(doom['next_issue']['number'], 2)
        self.assertEqual(doom['unread_count'], 2)
        self.assertEqual([r['state'] for r in doom['run']], ['read', 'owned', 'owned'])


class TestGetNext(InsightsTestCase):
    def test_closest_to_done_ordering(self):
        self.add_series('Hitman', [{'number': n, 'owned': True, 'bought': ago(800)} for n in range(1, 7)]
                        + [{'number': 7, 'owned': False}])
        self.add_series('Martian Manhunter', [
            {'number': 1, 'owned': True, 'read': True, 'bought': ago(100), 'read_at': ago(90)},
            {'number': 2, 'owned': False},
        ])
        self.add_series('Batman', [{'number': 1, 'owned': True, 'bought': ago(200)},
                                   {'number': 2, 'owned': False}, {'number': 3, 'owned': False}])
        self.add_series('Hellblazer', [{'number': 1, 'owned': False}])
        self.add_series('Done', [{'number': 1, 'owned': True}, {'number': 2, 'owned': True}])

        rv = self.client.get('/api/insights/get-next')
        self.assertEqual(rv.status_code, 200)
        titles = [row['series']['title'] for row in rv.json['items']]
        self.assertEqual(titles, ['Martian Manhunter', 'Hitman', 'Batman'])
        self.assertEqual(rv.json['one_away'], 2)
        first = rv.json['items'][0]
        self.assertTrue(first['caught_up'])
        self.assertEqual(first['next_missing'], 2)
        self.assertEqual(rv.json['items'][2]['missing_count'], 2)
        self.assertEqual(rv.json['unstarted'], {'count': 1, 'titles': ['Hellblazer']})
        self.assertNotIn('estimated_cost', first)


class TestActivity(InsightsTestCase):
    def test_zero_filled_months_and_figures(self):
        now = datetime.now()
        self.add_series('Akira', [
            {'number': 1, 'owned': True, 'read': True, 'bought': this_year(1), 'read_at': ago(10)},
            {'number': 2, 'owned': True, 'bought': this_year(1)},
            {'number': 3, 'owned': True, 'bought': ago(700)},
        ])
        rv = self.client.get('/api/insights/activity?range=ytd')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['range'], 'ytd')
        self.assertEqual(rv.json['mode'], 'month')
        self.assertEqual(len(rv.json['buckets']), now.month)
        self.assertTrue(all(b['key'].startswith(f'{now.year}-') for b in rv.json['buckets']))
        self.assertEqual(rv.json['totals']['bought'], 2)
        self.assertTrue(all({'key', 'label', 'bought', 'read'} <= set(b) for b in rv.json['buckets']))

        figures = rv.json['figures']
        self.assertEqual(figures['unread'], {'count': 2, 'series_count': 1})
        self.assertEqual(figures['last_read']['issue']['number'], 1)
        self.assertEqual(figures['last_read']['days'], 10)
        self.assertIsNone(figures['bought_to_read'])
        self.assertEqual(figures['waiting_longest']['issue']['number'], 3)
        self.assertEqual(figures['waiting_longest']['days'], 700)

        rv = self.client.get('/api/insights/activity?range=all')
        self.assertEqual(rv.json['mode'], 'year')
        self.assertEqual(rv.json['buckets'][-1]['key'], str(datetime.now().year))

    def test_last_year_is_the_full_previous_calendar_year(self):
        then = last_year_today()
        self.add_series('Berserk', [
            {'number': 1, 'owned': True, 'read': True, 'bought': then, 'read_at': then},
            {'number': 2, 'owned': True, 'bought': this_year(1)},
        ])
        rv = self.client.get('/api/insights/activity?range=last_year')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['range'], 'last_year')
        self.assertEqual(rv.json['mode'], 'month')
        self.assertEqual([b['key'] for b in rv.json['buckets']], [f'{then.year}-{m:02d}' for m in range(1, 13)])
        self.assertEqual(rv.json['totals'], {'bought': 1, 'read': 1})

    def test_unknown_range_falls_back(self):
        rv = self.client.get('/api/insights/activity?range=bogus')
        self.assertEqual(rv.json['range'], 'ytd')


class TestRecords(InsightsTestCase):
    def test_completed_runs_records_and_single_volumes(self):
        self.add_series('Sandman', [
            {'number': 1, 'owned': True, 'read': True, 'bought': ago(300), 'read_at': ago(200)},
            {'number': 2, 'owned': True, 'read': True, 'bought': ago(250), 'read_at': ago(100)},
        ])
        self.add_series('Mask', [{'number': 1, 'owned': True, 'bought': ago(50)},
                                 {'number': 2, 'owned': True, 'bought': ago(50)}])
        self.add_series('Single read', [{'number': 1, 'owned': True, 'read': True, 'read_at': ago(400)}])
        self.add_series('Single unread', [{'number': 1, 'owned': True}])

        rv = self.client.get('/api/insights/records')
        self.assertEqual(rv.status_code, 200)
        completed = rv.json['completed']
        self.assertEqual([(c['series']['title'], c['status']) for c in completed],
                         [('Mask', 'collected'), ('Sandman', 'both')])
        self.assertEqual(rv.json['single_volumes'], {'count': 2, 'owned': 2, 'read': 1})
        self.assertEqual(rv.json['firsts']['first_read']['series']['title'], 'Single read')
        self.assertEqual(rv.json['firsts']['first_purchase']['series']['title'], 'Sandman')
        self.assertIsNotNone(rv.json['firsts']['on_vertigo_since'])
        # two purchases in one month is below the minimum of three
        self.assertIsNone(rv.json['records']['biggest_buying_month'])
        self.assertIsNone(rv.json['records']['longest_complete_run'])

    def test_biggest_month_needs_three(self):
        self.add_series('Bulk', [{'number': n, 'owned': True, 'bought': ago(3)} for n in range(1, 4)])
        rv = self.client.get('/api/insights/records')
        self.assertEqual(rv.json['records']['biggest_buying_month']['count'], 3)


class TestFacts(InsightsTestCase):
    def test_on_this_day_exact_match(self):
        self.add_series('Reptilian', [{'number': 1, 'owned': True, 'bought': last_year_today()}])
        self.add_series('Filler', [{'number': 1, 'owned': True, 'bought': ago(100)}])
        rv = self.client.get('/api/insights/facts')
        self.assertEqual(rv.status_code, 200)
        otd = rv.json['on_this_day']
        self.assertIsNotNone(otd)
        self.assertEqual(otd['scope'], 'day')
        self.assertEqual(otd['groups'][0]['kind'], 'bought')
        self.assertEqual(otd['groups'][0]['items'][0]['label'], 'Reptilian')

    def test_on_this_day_hidden_without_events_and_facts_need_two(self):
        self.add_series('Only', [{'number': 1, 'owned': True, 'bought': ago(10)}])
        rv = self.client.get('/api/insights/facts')
        self.assertIsNone(rv.json['on_this_day'])
        # this_year is eligible, nothing else: below the minimum of two facts
        self.assertEqual(rv.json['facts'], [])

    def test_facts_are_stable_for_the_day(self):
        for n in range(6):
            self.add_series(f'Series {n}', [{'number': 1, 'owned': True, 'bought': ago(5 + n)},
                                            {'number': 2, 'owned': False}])
        self.add_series('Unstarted', [{'number': 1, 'owned': False}])
        first = self.client.get('/api/insights/facts').json['facts']
        second = self.client.get('/api/insights/facts').json['facts']
        self.assertEqual([f['id'] for f in first], [f['id'] for f in second])
        ids = {f['id'] for f in first}
        self.assertIn('unstarted_series', ids)
        self.assertIn('this_year', ids)
