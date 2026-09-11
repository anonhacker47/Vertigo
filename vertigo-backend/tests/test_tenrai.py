import json
import unittest
from unittest.mock import MagicMock, patch

import requests

from api.integrations.tenrai import client as tenrai_client
from api.integrations.tenrai import utils as tenrai_utils
from tests.base_test_case import BaseTestCase


def _http_error(status, headers=None, body=None):
    resp = requests.Response()
    resp.status_code = status
    resp.headers.update(headers or {})
    if body is not None:
        resp._content = json.dumps(body).encode()
    return requests.exceptions.HTTPError(f"{status} error", response=resp)


def _patch_session(**side_effects):
    session = MagicMock()
    for name, side_effect in side_effects.items():
        getattr(session, name).side_effect = side_effect
    return patch(
        'api.integrations.tenrai.tenrai_routes.get_tenrai_session',
        return_value=session,
    )


def _manga(**overrides):
    m = {
        'mal_id': 2,
        'title': 'Berserk',
        'published': {'from': '1989-08-25T00:00:00+00:00', 'to': None},
        'chapters': None,
        'volumes': None,
        'status': 'Publishing',
        'synopsis': 'Guts.',
        'url': 'https://myanimelist.net/manga/2/Berserk',
        'images': {
            'jpg': {'large_image_url': 'https://img/berserk.jpg'},
            'webp': {'large_image_url': 'https://img/berserk.webp'},
        },
        'publishers': None,
        'serializations': [{'mal_id': 2, 'type': 'manga', 'name': 'Young Animal'}],
        'authors': [{'mal_id': 1868, 'name': 'Miura, Kentarou', 'role': 'Story & Art'}],
        'genres': [{'mal_id': 1, 'name': 'Action'}],
    }
    m.update(overrides)
    return m


class TestTenraiRoutes(BaseTestCase):
    def test_search_success(self):
        session = MagicMock()
        session.search_manga.return_value = [_manga()]
        with patch('api.integrations.tenrai.tenrai_routes.get_tenrai_session',
                   return_value=session):
            rv = self.client.get('/api/tenrai/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['total_found'], 1)
        item = rv.json['items'][0]
        self.assertEqual(item['name'], 'Berserk')
        self.assertEqual(item['year_began'], '1989')
        self.assertEqual(item['image_url'], 'https://img/berserk.webp')

    def test_search_tolerates_null_fields(self):
        # Tenrai returns null for unknown scalars; must not crash on slicing.
        session = MagicMock()
        session.search_manga.return_value = [
            _manga(published={'from': None, 'to': None}, images=None, genres=None),
        ]
        with patch('api.integrations.tenrai.tenrai_routes.get_tenrai_session',
                   return_value=session):
            rv = self.client.get('/api/tenrai/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 200)
        self.assertIsNone(rv.json['items'][0]['year_began'])
        self.assertIsNone(rv.json['items'][0]['image_url'])

    def test_search_upstream_5xx_returns_502(self):
        with _patch_session(search_manga=_http_error(504)):
            rv = self.client.get('/api/tenrai/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 502)
        self.assertEqual(rv.json['error'], 'tenrai_error')
        self.assertEqual(rv.json['upstream_status'], 504)

    def test_search_rate_limited_returns_429(self):
        with _patch_session(search_manga=_http_error(429, {'Retry-After': '3'})):
            rv = self.client.get('/api/tenrai/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 429)
        self.assertEqual(rv.json['error'], 'rate_limited')
        self.assertEqual(rv.json['retry_after'], 3)

    def test_search_blocked_403_returns_502_with_hint(self):
        with _patch_session(search_manga=_http_error(403)):
            rv = self.client.get('/api/tenrai/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 502)
        self.assertEqual(rv.json['error'], 'tenrai_error')
        self.assertIn('24 hours', rv.json['message'])

    def test_search_timeout_returns_504(self):
        with _patch_session(search_manga=requests.exceptions.ConnectTimeout('slow')):
            rv = self.client.get('/api/tenrai/manga/search?query=Berserk')

        self.assertEqual(rv.status_code, 504)
        self.assertEqual(rv.json['error'], 'tenrai_unavailable')

    def test_detail_success_uses_serialization_as_publisher(self):
        session = MagicMock()
        session.manga.return_value = _manga()
        with patch('api.integrations.tenrai.tenrai_routes.get_tenrai_session',
                   return_value=session):
            rv = self.client.get('/api/tenrai/manga/2')

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['publisher'], {'mal_id': 2, 'value': 'Young Animal'})
        self.assertEqual(rv.json['genres'], [{'mal_id': 1, 'value': 'Action'}])
        self.assertEqual(rv.json['image_url'], 'https://img/berserk.jpg')
        self.assertEqual(rv.json['mal_url'], 'https://myanimelist.net/manga/2/Berserk')

    def test_detail_without_serialization_has_no_publisher(self):
        session = MagicMock()
        session.manga.return_value = _manga(serializations=[])
        with patch('api.integrations.tenrai.tenrai_routes.get_tenrai_session',
                   return_value=session):
            rv = self.client.get('/api/tenrai/manga/2')

        self.assertEqual(rv.status_code, 200)
        self.assertIsNone(rv.json['publisher'])

    def test_detail_upstream_error_returns_502(self):
        with _patch_session(manga=_http_error(502)):
            rv = self.client.get('/api/tenrai/manga/2')

        self.assertEqual(rv.status_code, 502)
        self.assertEqual(rv.json['error'], 'tenrai_error')

    def test_detail_upstream_404_returns_404_with_message(self):
        body = {
            'status': 404,
            'type': 'ResourceNotFoundException',
            'message': 'Manga with ID 999999 not found.',
        }
        with _patch_session(manga=_http_error(404, body=body)):
            rv = self.client.get('/api/tenrai/manga/999999')

        self.assertEqual(rv.status_code, 404)
        self.assertEqual(rv.json['error'], 'not_found')
        self.assertEqual(rv.json['message'], 'Manga with ID 999999 not found.')

    def test_detail_missing_manga_returns_404(self):
        session = MagicMock()
        session.manga.return_value = None
        with patch('api.integrations.tenrai.tenrai_routes.get_tenrai_session',
                   return_value=session):
            rv = self.client.get('/api/tenrai/manga/999999')

        self.assertEqual(rv.status_code, 404)
        self.assertEqual(rv.json['error'], 'not_found')

    def test_entities_success(self):
        session = MagicMock()
        session.manga_characters.return_value = [
            {'character': {'mal_id': 422, 'name': 'Guts'}, 'role': 'Main'},
            {'character': {'mal_id': 423, 'name': 'Casca'}, 'role': 'Main'},
        ]
        session.manga.return_value = _manga()
        with patch('api.integrations.tenrai.tenrai_routes.get_tenrai_session',
                   return_value=session):
            rv = self.client.get('/api/tenrai/manga/2/entities')

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['total_characters'], 2)
        self.assertEqual(rv.json['characters'][0], {'mal_id': 422, 'value': 'Guts'})
        self.assertEqual(rv.json['total_creators'], 1)
        self.assertEqual(rv.json['creators'][0], {'mal_id': 1868, 'value': 'Miura, Kentarou'})

    def test_entities_upstream_error_returns_502(self):
        with _patch_session(manga_characters=_http_error(500)):
            rv = self.client.get('/api/tenrai/manga/2/entities')

        self.assertEqual(rv.status_code, 502)
        self.assertEqual(rv.json['error'], 'tenrai_error')


class TestTenraiSessionConfig(BaseTestCase):
    def test_server_key_sent_as_header_when_configured(self):
        self.app.config['TENRAI_SERVER_KEY'] = 'secret-key'
        with self.app.test_request_context():
            session = tenrai_client.get_tenrai_session()

        self.assertEqual(session.session.headers.get('X-Server-Key'), 'secret-key')
        self.assertEqual(session.session.headers.get('User-Agent'), 'Vertigo/Tenrai')

    def test_no_server_key_header_by_default(self):
        self.app.config['TENRAI_SERVER_KEY'] = None
        with self.app.test_request_context():
            session = tenrai_client.get_tenrai_session()

        self.assertNotIn('X-Server-Key', session.session.headers)
        self.assertEqual(session.base_url, 'https://api.tenrai.org/v1')


class TestTenraiClientRetry(unittest.TestCase):
    def setUp(self):
        self.tenrai = tenrai_client.TenraiSession()

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
        with patch.object(self.tenrai.session, 'get', side_effect=responses) as get, \
                patch.object(tenrai_client.time, 'sleep') as sleep:
            result = self.tenrai._get('/manga', {'q': 'Berserk'})

        self.assertEqual(result, [{'mal_id': 2}])
        self.assertEqual(get.call_count, 2)
        sleep.assert_called_once_with(tenrai_client.RETRY_BACKOFF_SECONDS)

    def test_gives_up_after_max_retries(self):
        responses = [self._response(504)] * (tenrai_client.MAX_RETRIES + 1)
        with patch.object(self.tenrai.session, 'get', side_effect=responses) as get, \
                patch.object(tenrai_client.time, 'sleep'):
            with self.assertRaises(requests.exceptions.HTTPError) as ctx:
                self.tenrai._get('/manga', {'q': 'Berserk'})

        self.assertEqual(ctx.exception.response.status_code, 504)
        self.assertEqual(get.call_count, tenrai_client.MAX_RETRIES + 1)

    def test_does_not_retry_on_4xx(self):
        with patch.object(self.tenrai.session, 'get',
                          return_value=self._response(429)) as get, \
                patch.object(tenrai_client.time, 'sleep') as sleep:
            with self.assertRaises(requests.exceptions.HTTPError):
                self.tenrai._get('/manga', {'q': 'Berserk'})

        self.assertEqual(get.call_count, 1)
        sleep.assert_not_called()

    def test_retries_on_timeout(self):
        responses = [requests.exceptions.ReadTimeout('slow'),
                     self._response(200, [])]
        with patch.object(self.tenrai.session, 'get', side_effect=responses) as get, \
                patch.object(tenrai_client.time, 'sleep'):
            result = self.tenrai._get('/manga', {'q': 'Berserk'})

        self.assertEqual(result, [])
        self.assertEqual(get.call_count, 2)

    def test_requests_hit_v1_paths(self):
        with patch.object(self.tenrai.session, 'get',
                          return_value=self._response(200, {})) as get:
            self.tenrai.person(1868)
            self.tenrai.character(422)
            self.tenrai.manga_characters(2)

        called = [c.args[0] for c in get.call_args_list]
        self.assertEqual(called, [
            'https://api.tenrai.org/v1/people/1868',
            'https://api.tenrai.org/v1/characters/422',
            'https://api.tenrai.org/v1/manga/2/characters',
        ])


class TestFetchTenraiEntityInfo(BaseTestCase):
    def _run(self, entity_type, mal_id, session, **kwargs):
        with patch('api.integrations.tenrai.utils.get_tenrai_session', return_value=session), \
                patch('api.integrations.tenrai.utils.wait_for_tenrai_slot') as wait:
            result = tenrai_utils.fetch_tenrai_entity_info(entity_type, mal_id, **kwargs)
        return result, wait

    def test_creator_fetches_person(self):
        session = MagicMock()
        session.person.return_value = {'mal_id': 1868, 'about': 'Mangaka'}

        result, _ = self._run('creator', 1868, session)

        self.assertEqual(result['about'], 'Mangaka')
        session.person.assert_called_once_with(1868)

    def test_character_fetches_character(self):
        session = MagicMock()
        session.character.return_value = {'mal_id': 422, 'about': 'Guts'}

        result, _ = self._run('character', 422, session)

        self.assertEqual(result['about'], 'Guts')
        session.character.assert_called_once_with(422)

    def test_publisher_skips_request(self):
        # Tenrai has no per-magazine endpoint, so there is nothing to fetch.
        session = MagicMock()

        result, wait = self._run('publisher', 2, session)

        self.assertIsNone(result)
        session.assert_not_called()
        wait.assert_not_called()

    def test_429_honours_retry_after_header_then_succeeds(self):
        session = MagicMock()
        session.person.side_effect = [
            _http_error(429, {'Retry-After': '7'}),
            {'mal_id': 1868},
        ]

        result, wait = self._run('creator', 1868, session)

        self.assertEqual(result, {'mal_id': 1868})
        self.assertEqual(session.person.call_count, 2)
        wait.assert_any_call(7)

    def test_gives_up_after_repeated_429(self):
        session = MagicMock()
        session.person.side_effect = _http_error(429)

        result, _ = self._run('creator', 1868, session, max_retries=1)

        self.assertIsNone(result)
        self.assertEqual(session.person.call_count, 2)

    def test_non_429_http_error_returns_none(self):
        session = MagicMock()
        session.person.side_effect = _http_error(404)

        result, _ = self._run('creator', 1868, session)

        self.assertIsNone(result)
        session.person.assert_called_once()


if __name__ == '__main__':
    unittest.main()
