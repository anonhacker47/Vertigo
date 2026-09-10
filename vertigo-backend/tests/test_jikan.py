import unittest
from unittest.mock import MagicMock, patch

import requests

from api.integrations.jikan import client as jikan_client
from tests.base_test_case import BaseTestCase


def _http_error(status, headers=None):
    resp = requests.Response()
    resp.status_code = status
    resp.headers.update(headers or {})
    return requests.exceptions.HTTPError(f"{status} error", response=resp)


def _patch_session(**side_effects):
    session = MagicMock()
    for name, side_effect in side_effects.items():
        getattr(session, name).side_effect = side_effect
    return patch(
        'api.integrations.jikan.jikan_routes.get_jikan_session',
        return_value=session,
    )


class TestJikanRoutes(BaseTestCase):
    def test_search_success(self):
        session = MagicMock()
        session.search_manga.return_value = [{
            'mal_id': 2,
            'title': 'Berserk',
            'published': {'from': '1989-08-25T00:00:00+00:00'},
            'chapters': None,
            'volumes': None,
            'images': {'webp': {'large_image_url': 'https://img/berserk.webp'}},
        }]
        with patch('api.integrations.jikan.jikan_routes.get_jikan_session',
                   return_value=session):
            rv = self.client.get('/api/jikan/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['total_found'], 1)
        self.assertEqual(rv.json['items'][0]['name'], 'Berserk')
        self.assertEqual(rv.json['items'][0]['year_began'], '1989')

    def test_search_upstream_5xx_returns_502(self):
        with _patch_session(search_manga=_http_error(504)):
            rv = self.client.get('/api/jikan/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 502)
        self.assertEqual(rv.json['error'], 'jikan_error')
        self.assertEqual(rv.json['upstream_status'], 504)

    def test_search_rate_limited_returns_429(self):
        with _patch_session(search_manga=_http_error(429, {'Retry-After': '3'})):
            rv = self.client.get('/api/jikan/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 429)
        self.assertEqual(rv.json['error'], 'rate_limited')
        self.assertEqual(rv.json['retry_after'], 3)

    def test_search_timeout_returns_504(self):
        with _patch_session(search_manga=requests.exceptions.ConnectTimeout('slow')):
            rv = self.client.get('/api/jikan/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 504)
        self.assertEqual(rv.json['error'], 'jikan_unavailable')

    def test_detail_upstream_error_returns_502(self):
        with _patch_session(manga=_http_error(502)):
            rv = self.client.get('/api/jikan/manga/2')

        self.assertEqual(rv.status_code, 502)
        self.assertEqual(rv.json['error'], 'jikan_error')

    def test_detail_missing_manga_returns_404(self):
        session = MagicMock()
        session.manga.return_value = None
        with patch('api.integrations.jikan.jikan_routes.get_jikan_session',
                   return_value=session):
            rv = self.client.get('/api/jikan/manga/999999')

        self.assertEqual(rv.status_code, 404)
        self.assertEqual(rv.json['error'], 'not_found')

    def test_entities_upstream_error_returns_502(self):
        with _patch_session(manga_characters=_http_error(500)):
            rv = self.client.get('/api/jikan/manga/2/entities')

        self.assertEqual(rv.status_code, 502)
        self.assertEqual(rv.json['error'], 'jikan_error')


class TestJikanClientRetry(unittest.TestCase):
    def setUp(self):
        self.jikan = jikan_client.JikanSession()

    @staticmethod
    def _response(status=200, data=None):
        resp = MagicMock()
        if status >= 400:
            resp.raise_for_status.side_effect = _http_error(status)
        else:
            resp.raise_for_status.return_value = None
        resp.json.return_value = {'data': data}
        return resp

    def test_retries_once_on_504_then_succeeds(self):
        responses = [self._response(504), self._response(200, [{'mal_id': 2}])]
        with patch.object(self.jikan.session, 'get', side_effect=responses) as get, \
                patch.object(jikan_client.time, 'sleep') as sleep:
            result = self.jikan._get('/manga', {'q': 'Berserk'})

        self.assertEqual(result, [{'mal_id': 2}])
        self.assertEqual(get.call_count, 2)
        sleep.assert_called_once_with(jikan_client.RETRY_BACKOFF_SECONDS)

    def test_gives_up_after_max_retries(self):
        responses = [self._response(504)] * (jikan_client.MAX_RETRIES + 1)
        with patch.object(self.jikan.session, 'get', side_effect=responses) as get, \
                patch.object(jikan_client.time, 'sleep'):
            with self.assertRaises(requests.exceptions.HTTPError) as ctx:
                self.jikan._get('/manga', {'q': 'Berserk'})

        self.assertEqual(ctx.exception.response.status_code, 504)
        self.assertEqual(get.call_count, jikan_client.MAX_RETRIES + 1)

    def test_does_not_retry_on_4xx(self):
        with patch.object(self.jikan.session, 'get',
                          return_value=self._response(429)) as get, \
                patch.object(jikan_client.time, 'sleep') as sleep:
            with self.assertRaises(requests.exceptions.HTTPError):
                self.jikan._get('/manga', {'q': 'Berserk'})

        self.assertEqual(get.call_count, 1)
        sleep.assert_not_called()

    def test_retries_on_timeout(self):
        responses = [requests.exceptions.ReadTimeout('slow'),
                     self._response(200, [])]
        with patch.object(self.jikan.session, 'get', side_effect=responses) as get, \
                patch.object(jikan_client.time, 'sleep'):
            result = self.jikan._get('/manga', {'q': 'Berserk'})

        self.assertEqual(result, [])
        self.assertEqual(get.call_count, 2)


if __name__ == '__main__':
    unittest.main()
