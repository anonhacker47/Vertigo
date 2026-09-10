import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests
from mokkari.exceptions import ApiError, RateLimitError

from api.integrations.mokkari import mokkari_routes
from api.integrations.mokkari.mokkari_rate_limiter import retry_after_seconds
from tests.base_test_case import BaseTestCase


def _rate_limit_error(retry_after=None,
                      message="Metron API Rate Limit exceeded, need to wait for 28 seconds."):
    """Build the exception exactly the way mokkari raises it."""
    err = RateLimitError(message)
    if retry_after is not None:
        resp = requests.Response()
        resp.status_code = 429
        resp.headers["Retry-After"] = str(retry_after)
        err.__cause__ = requests.exceptions.HTTPError("429", response=resp)
    return err


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
    def test_prefers_header(self):
        self.assertEqual(retry_after_seconds(_rate_limit_error(retry_after=28)), 28)

    def test_parses_message_when_no_header(self):
        err = _rate_limit_error(message="need to wait for 1 minute, 5 seconds.")
        self.assertEqual(retry_after_seconds(err), 65)

    def test_default_when_nothing_to_parse(self):
        self.assertEqual(retry_after_seconds(RateLimitError("nope"), default=40), 40)
        self.assertIsNone(retry_after_seconds(RateLimitError("nope")))


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
        patches = [
            patch('api.integrations.mokkari.mokkari_routes.get_mokkari_session',
                  return_value=self.session),
            patch('api.integrations.mokkari.mokkari_routes.wait_for_mokkari_slot'),
            patch('api.integrations.mokkari.mokkari_routes.note_rate_limit'),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

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
        self.session.issues_list.side_effect = _rate_limit_error()
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
