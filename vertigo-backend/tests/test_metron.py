import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from mokkari.exceptions import ApiError, RateLimitError

from api.integrations.mokkari import mokkari_routes
from api.integrations.mokkari.status import retry_after_seconds
from tests.base_test_case import BaseTestCase


def _rate_limit_error(retry_after=28,
                      message="Metron API Rate Limit exceeded, need to wait for 28 seconds."):
    return RateLimitError(message, retry_after=retry_after)


def _stub(i):
    return SimpleNamespace(id=1000 + i, number=str(i), image=f"https://img/{i}.jpg")


def _detail(i):
    return SimpleNamespace(
        resource_url=f"https://metron.cloud/issue/watchmen-1986-{i}/",
        credits=[SimpleNamespace(id=5, creator="Alan Moore"),
                 SimpleNamespace(id=6, creator="Dave Gibbons")],
        characters=[SimpleNamespace(id=9, name="Rorschach"),
                    SimpleNamespace(id=10 + i, name=f"Extra {i}")],
    )


class TestRetryAfterSeconds(unittest.TestCase):
    def test_rounds_up_to_whole_seconds(self):
        self.assertEqual(retry_after_seconds(_rate_limit_error(retry_after=28)), 28)
        self.assertEqual(retry_after_seconds(_rate_limit_error(retry_after=27.2)), 28)

    def test_none_when_mokkari_reports_no_wait(self):
        self.assertIsNone(retry_after_seconds(RateLimitError("nope")))
        self.assertIsNone(retry_after_seconds(ApiError("nope")))


class TestIssueUrl(unittest.TestCase):
    def test_builds_from_series_slug(self):
        self.assertEqual(
            mokkari_routes._issue_url("https://metron.cloud/series/watchmen-1986/", "1"),
            "https://metron.cloud/issue/watchmen-1986-1/")

    def test_slugifies_number(self):
        self.assertEqual(
            mokkari_routes._issue_url("https://metron.cloud/series/x-1990/", "1.5"),
            "https://metron.cloud/issue/x-1990-15/")

    def test_none_without_series_url(self):
        self.assertIsNone(mokkari_routes._issue_url(None, "1"))


class TestMetronRoutes(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.session = MagicMock()
        self.session.series.return_value = SimpleNamespace(
            resource_url="https://metron.cloud/series/watchmen-1986/")
        self.get_session = patch(
            'api.integrations.mokkari.mokkari_routes.get_mokkari_session',
            return_value=self.session)
        self.get_session.start()
        self.addCleanup(self.get_session.stop)

    def test_without_a_token_every_route_says_not_configured(self):
        self.get_session.stop()
        with patch('api.integrations.mokkari.mokkari_routes.get_mokkari_session',
                   return_value=None):
            for url in ('/api/metron/series/search?query=Watchmen',
                        '/api/metron/series/564',
                        '/api/metron/series/564/entities'):
                rv = self.client.get(url)
                self.assertEqual(rv.status_code, 503, url)
                self.assertEqual(rv.json['error'], 'not_configured')
        self.get_session.start()

    def test_search_rate_limited_returns_429_with_retry_after(self):
        self.session.series_list.side_effect = _rate_limit_error(retry_after=28)
        rv = self.client.get('/api/metron/series/search?query=Watchmen')

        self.assertEqual(rv.status_code, 429)
        self.assertEqual(rv.json['error'], 'rate_limited')
        self.assertEqual(rv.json['retry_after'], 28)

    def test_entities_samples_first_issues_only(self):
        self.session.issues_list.return_value = [_stub(i) for i in range(1, 26)]
        self.session.issue.side_effect = lambda issue_id: _detail(issue_id - 1000)

        rv = self.client.get('/api/metron/series/564/entities')

        self.assertEqual(rv.status_code, 200)
        body = rv.json
        self.assertEqual(body['total_issues'], 25)
        self.assertEqual(body['sampled_issues'], mokkari_routes.ENTITY_SAMPLE_ISSUES)
        self.assertEqual(self.session.issue.call_count, mokkari_routes.ENTITY_SAMPLE_ISSUES)
        self.assertFalse(body['partial'])
        self.assertEqual({c['value'] for c in body['creators']}, {'Alan Moore', 'Dave Gibbons'})
        self.assertIn('Rorschach', {c['value'] for c in body['characters']})
        self.assertEqual(body['total_characters'], 1 + mokkari_routes.ENTITY_SAMPLE_ISSUES)

        by_number = {i['number']: i for i in body['issues']}
        # sampled issue: real URL from the detail; unsampled: derived from the series slug
        self.assertEqual(by_number['1']['metron_url'], 'https://metron.cloud/issue/watchmen-1986-1/')
        self.assertEqual(by_number['25']['metron_url'], 'https://metron.cloud/issue/watchmen-1986-25/')
        self.assertEqual(by_number['25']['image'], 'https://img/25.jpg')
        self.assertEqual(by_number['25']['metron_id'], 1025)

    def test_entities_partial_when_rate_limited_mid_scan(self):
        self.session.issues_list.return_value = [_stub(i) for i in range(1, 6)]
        self.session.issue.side_effect = [_detail(1), _detail(2), _rate_limit_error(retry_after=30)]

        rv = self.client.get('/api/metron/series/564/entities')

        self.assertEqual(rv.status_code, 200)
        body = rv.json
        self.assertTrue(body['partial'])
        self.assertEqual(body['retry_after'], 30)
        self.assertEqual(body['sampled_issues'], 2)
        self.assertEqual(body['total_issues'], 5)
        self.assertEqual(len(body['issues']), 5)
        self.assertEqual({c['value'] for c in body['creators']}, {'Alan Moore', 'Dave Gibbons'})

    def test_entities_rate_limited_before_issue_list_returns_429(self):
        self.session.issues_list.side_effect = _rate_limit_error(retry_after=28)
        rv = self.client.get('/api/metron/series/564/entities')

        self.assertEqual(rv.status_code, 429)
        self.assertEqual(rv.json['retry_after'], 28)

    def test_entities_api_error_returns_502(self):
        self.session.issues_list.side_effect = ApiError('boom')
        rv = self.client.get('/api/metron/series/564/entities')

        self.assertEqual(rv.status_code, 502)
        self.assertEqual(rv.json['error'], 'metron_error')

    def test_entities_skips_issue_that_errors(self):
        self.session.issues_list.return_value = [_stub(1), _stub(2)]
        self.session.issue.side_effect = [ApiError('gone'), _detail(2)]

        rv = self.client.get('/api/metron/series/564/entities')

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['sampled_issues'], 1)
        self.assertFalse(rv.json['partial'])


if __name__ == '__main__':
    unittest.main()
