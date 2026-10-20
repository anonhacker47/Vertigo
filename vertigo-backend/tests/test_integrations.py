import unittest
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import patch

import requests
from mokkari.exceptions import ApiError, RateLimitError
from mokkari.rate_limit import RateLimitStatus, RateLimitWindow

from api import db
from api.integrations.mokkari import client as mokkari_client
from api.integrations.mokkari import status as mokkari_status
from api.integrations.mokkari.credentials import mask_token, resolve_metron_token
from api.models.user import User
from tests.base_test_case import BaseTestCase

RATE_LIMIT = {
    "burst": {"limit": 20, "remaining": 19, "reset": "2026-10-20T13:00:00+00:00"},
    "sustained": {"limit": 5000, "remaining": 4990, "reset": "2026-10-21T00:00:00+00:00"},
}


def _api_error(status):
    resp = requests.Response()
    resp.status_code = status
    err = ApiError(f"HTTP error: {status}")
    err.__cause__ = requests.exceptions.HTTPError(str(status), response=resp)
    return err


class TestCredentials(unittest.TestCase):
    def test_mask_keeps_only_the_tail(self):
        self.assertEqual(mask_token("abcdefghijkl"), "••••ijkl")
        self.assertEqual(mask_token("short"), "••••")
        self.assertIsNone(mask_token(None))


class TestResolveToken(BaseTestCase):
    def test_user_token_beats_server_token(self):
        self.app.config['METRON_API_TOKEN'] = 'server-token'
        user = SimpleNamespace(metron_api_token='  user-token ')
        self.assertEqual(resolve_metron_token(user), ('user-token', 'user'))

    def test_falls_back_to_server_token(self):
        self.app.config['METRON_API_TOKEN'] = 'server-token'
        self.assertEqual(resolve_metron_token(SimpleNamespace(metron_api_token='')),
                         ('server-token', 'server'))
        self.assertEqual(resolve_metron_token(None), ('server-token', 'server'))

    def test_nothing_configured(self):
        self.app.config['METRON_API_TOKEN'] = None
        self.assertEqual(resolve_metron_token(None), (None, None))


class TestCheckToken(BaseTestCase):
    def _session(self, side_effect=None, status=None):
        session = unittest.mock.MagicMock()
        session.__enter__.return_value = session
        session.series_type_list.side_effect = side_effect
        session.rate_limit_status = status or RateLimitStatus()
        return patch('api.integrations.mokkari.status.verification_session',
                     return_value=session)

    def test_reports_rate_limit_windows(self):
        reset = datetime(2026, 10, 21, tzinfo=UTC)
        status = RateLimitStatus(
            burst=RateLimitWindow(limit=20, remaining=19, reset=reset),
            sustained=RateLimitWindow(limit=5000, remaining=4990, reset=reset))
        with self._session(status=status):
            windows = mokkari_status.check_token('token')
        self.assertEqual(windows['burst']['remaining'], 19)
        self.assertEqual(windows['sustained']['limit'], 5000)
        self.assertEqual(windows['sustained']['reset'], reset.isoformat())

    def test_401_becomes_auth_error(self):
        with self._session(side_effect=_api_error(401)):
            with self.assertRaises(mokkari_status.MetronAuthError):
                mokkari_status.check_token('bad')

    def test_other_failures_pass_through(self):
        with self._session(side_effect=_api_error(503)):
            with self.assertRaises(ApiError):
                mokkari_status.check_token('token')


class TestIntegrationsRoutes(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app.config['METRON_API_TOKEN'] = None
        mokkari_client._sessions.clear()

    def test_status_when_nothing_is_configured(self):
        rv = self.client.get('/api/integrations')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['metron'], {
            'configured': False, 'source': None, 'token_hint': None,
            'server_token': False, 'rate_limit': None})
        self.assertTrue(rv.json['myanimelist']['configured'])

    def test_status_with_server_token_hides_the_token(self):
        self.app.config['METRON_API_TOKEN'] = 'server-token-xyz'
        rv = self.client.get('/api/integrations')
        metron = rv.json['metron']
        self.assertTrue(metron['configured'])
        self.assertEqual(metron['source'], 'server')
        self.assertIsNone(metron['token_hint'])
        self.assertTrue(metron['server_token'])

    def test_save_token_checks_it_and_stores_it(self):
        with patch('api.routes.integrations_routes.check_token',
                   return_value=RATE_LIMIT) as check:
            rv = self.client.put('/api/integrations/metron',
                                 json={'api_token': ' my-metron-token-1234 '})
        self.assertEqual(rv.status_code, 200)
        check.assert_called_once_with('my-metron-token-1234')
        metron = rv.json['metron']
        self.assertEqual(metron['source'], 'user')
        self.assertEqual(metron['token_hint'], '••••1234')
        self.assertEqual(metron['rate_limit'], RATE_LIMIT)
        self.assertEqual(db.session.get(User, 1).metron_api_token, 'my-metron-token-1234')

        rv = self.client.get('/api/me')
        self.assertNotIn('metron_api_token', rv.json)

    def test_rejected_token_is_not_stored(self):
        with patch('api.routes.integrations_routes.check_token',
                   side_effect=mokkari_status.MetronAuthError('401')):
            rv = self.client.put('/api/integrations/metron', json={'api_token': 'wrong-token-1'})
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(rv.json['error'], 'token_rejected')
        self.assertIsNone(db.session.get(User, 1).metron_api_token)

    def test_unreachable_metron_is_a_502(self):
        with patch('api.routes.integrations_routes.check_token',
                   side_effect=ApiError('Connection error')):
            rv = self.client.put('/api/integrations/metron', json={'api_token': 'some-token-1'})
        self.assertEqual(rv.status_code, 502)
        self.assertEqual(rv.json['error'], 'metron_error')

    def test_rate_limited_check_is_a_429(self):
        with patch('api.routes.integrations_routes.check_token',
                   side_effect=RateLimitError('slow down', retry_after=30)):
            rv = self.client.put('/api/integrations/metron', json={'api_token': 'some-token-1'})
        self.assertEqual(rv.status_code, 429)
        self.assertEqual(rv.json['retry_after'], 30)

    def test_malformed_tokens_are_rejected_without_asking_metron(self):
        with patch('api.routes.integrations_routes.check_token') as check:
            for bad in ('abc', 'abc\ndefghijk', 'tökén-abcdefgh', 'has space abcdef'):
                rv = self.client.put('/api/integrations/metron', json={'api_token': bad})
                self.assertEqual(rv.status_code, 400, repr(bad))
                self.assertEqual(rv.json['error'], 'invalid_token', repr(bad))
        check.assert_not_called()

    def test_clear_token_falls_back_to_server(self):
        user = db.session.get(User, 1)
        user.metron_api_token = 'user-token-1234'
        db.session.commit()
        self.app.config['METRON_API_TOKEN'] = 'server-token'

        rv = self.client.delete('/api/integrations/metron')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['metron']['source'], 'server')
        self.assertIsNone(db.session.get(User, 1).metron_api_token)

    def test_test_endpoint_without_token(self):
        rv = self.client.post('/api/integrations/metron/test')
        self.assertEqual(rv.status_code, 503)
        self.assertEqual(rv.json['error'], 'not_configured')

    def test_test_endpoint_reports_source_and_windows(self):
        self.app.config['METRON_API_TOKEN'] = 'server-token'
        with patch('api.routes.integrations_routes.check_token', return_value=RATE_LIMIT):
            rv = self.client.post('/api/integrations/metron/test')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json, {'ok': True, 'source': 'server', 'rate_limit': RATE_LIMIT})

    def test_test_endpoint_rejected_server_token(self):
        self.app.config['METRON_API_TOKEN'] = 'server-token'
        with patch('api.routes.integrations_routes.check_token',
                   side_effect=mokkari_status.MetronAuthError('401')):
            rv = self.client.post('/api/integrations/metron/test')
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(rv.json['error'], 'token_rejected')
        self.assertEqual(rv.json['source'], 'server')


class TestSessionRegistry(BaseTestCase):
    def setUp(self):
        super().setUp()
        mokkari_client._sessions.clear()

    def test_one_session_per_token_shared_across_calls(self):
        with patch.object(mokkari_client, '_build_session',
                          side_effect=lambda token, cache: SimpleNamespace(token=token)) as build:
            a = mokkari_client.session_for_token('tok-a')
            again = mokkari_client.session_for_token('tok-a')
            b = mokkari_client.session_for_token('tok-b')
        self.assertIs(a, again)
        self.assertIsNot(a, b)
        self.assertEqual(build.call_count, 2)

    def test_get_session_uses_the_users_token(self):
        user = db.session.get(User, 1)
        user.metron_api_token = 'user-token-1234'
        db.session.commit()
        with patch.object(mokkari_client, '_build_session',
                          side_effect=lambda token, cache: SimpleNamespace(token=token)):
            session = mokkari_client.get_mokkari_session(user)
        self.assertEqual(session.token, 'user-token-1234')

    def test_no_token_means_no_session(self):
        self.app.config['METRON_API_TOKEN'] = None
        self.assertIsNone(mokkari_client.get_mokkari_session(db.session.get(User, 1)))


if __name__ == '__main__':
    unittest.main()
