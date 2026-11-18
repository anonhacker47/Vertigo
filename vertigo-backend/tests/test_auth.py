from datetime import datetime, timedelta
from api import db
from api.models.token import Token
from tests.base_test_case import BaseTestCase, TestConfigWithAuth


def bearer(access_token):
    return {'Authorization': f'Bearer {access_token}'}


class AuthTests(BaseTestCase):
    config = TestConfigWithAuth

    def login(self, username='test', password='foo'):
        rv = self.client.post('/api/tokens', auth=(username, password))
        self.assertEqual(rv.status_code, 200)
        return rv.json['access_token'], rv.json['refresh_token']

    def me(self, access_token):
        return self.client.get('/api/me', headers=bearer(access_token)).status_code

    def refresh(self, access_token, refresh_token=None):
        body = {'access_token': access_token}
        if refresh_token is not None:
            body['refresh_token'] = refresh_token
        return self.client.put('/api/tokens', json=body)

    def test_no_auth(self):
        self.assertEqual(self.client.get('/api/me').status_code, 401)

    def test_get_token(self):
        access_token, refresh_token = self.login()
        rv = self.client.get('/api/me', headers=bearer(access_token))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['username'], 'test')
        self.assertEqual(self.me(access_token + 'x'), 401)
        self.assertEqual(self.me(refresh_token), 401)

    def test_login_with_email(self):
        access_token, _ = self.login('test@example.com')
        self.assertEqual(self.me(access_token), 200)

    def test_get_token_in_cookie_only(self):
        self.app.config['REFRESH_TOKEN_IN_COOKIE'] = True
        self.app.config['REFRESH_TOKEN_IN_BODY'] = False
        rv = self.client.post('/api/tokens', auth=('test', 'foo'))
        self.assertEqual(rv.status_code, 200)
        self.assertIsNone(rv.json['refresh_token'])
        self.assertTrue(rv.headers['Set-Cookie'].startswith('refresh_token='))

    def test_get_token_in_body_only(self):
        self.app.config['REFRESH_TOKEN_IN_COOKIE'] = False
        self.app.config['REFRESH_TOKEN_IN_BODY'] = True
        rv = self.client.post('/api/tokens', auth=('test', 'foo'))
        self.assertEqual(rv.status_code, 200)
        self.assertIsNotNone(rv.json['refresh_token'])
        self.assertNotIn('Set-Cookie', rv.headers)

    def test_token_expired(self):
        access_token, _ = self.login()
        token = Token.from_jwt(access_token)
        token.access_expiration = datetime.utcnow() - timedelta(minutes=1)
        db.session.commit()
        self.assertEqual(self.me(access_token), 401)

    def test_refresh_token_from_the_cookie(self):
        access_token1, refresh_token1 = self.login()
        rv = self.client.put('/api/tokens', json={'access_token': access_token1},
                             headers={'Cookie': 'refresh_token=' + refresh_token1})
        self.assertEqual(rv.status_code, 200)
        self.assertNotEqual(rv.json['access_token'], access_token1)
        self.assertNotEqual(rv.json['refresh_token'], refresh_token1)
        self.assertEqual(self.me(rv.json['access_token']), 200)
        self.assertEqual(self.me(access_token1), 401)

    def test_refresh_token_failure(self):
        self.app.config['REFRESH_TOKEN_IN_COOKIE'] = False
        access_token, refresh_token = self.login()
        self.assertEqual(self.refresh(access_token).status_code, 401)
        self.assertEqual(self.refresh(access_token, refresh_token + 'x').status_code, 401)
        self.assertEqual(self.refresh(access_token + 'x', refresh_token).status_code, 401)
        self.assertEqual(self.refresh('foo', refresh_token).status_code, 401)

    def test_reusing_a_refresh_token_revokes_every_session(self):
        self.app.config['REFRESH_TOKEN_IN_COOKIE'] = False
        access_token1, refresh_token1 = self.login()
        access_token2, refresh_token2 = self.login()

        rv = self.refresh(access_token2, refresh_token2)
        self.assertEqual(rv.status_code, 200)
        access_token3, refresh_token3 = rv.json['access_token'], rv.json['refresh_token']

        self.assertEqual(self.refresh(access_token2, refresh_token2).status_code, 401)

        for access_token, refresh_token in ((access_token1, refresh_token1), (access_token2, refresh_token2),
                                            (access_token3, refresh_token3)):
            self.assertEqual(self.me(access_token), 401)
            self.assertEqual(self.refresh(access_token, refresh_token).status_code, 401)

    def test_revoke(self):
        access_token, _ = self.login()
        self.assertEqual(self.me(access_token), 200)
        rv = self.client.delete('/api/tokens', headers=bearer(access_token))
        self.assertEqual(rv.status_code, 204)
        self.assertEqual(self.me(access_token), 401)

    def test_no_login(self):
        self.assertEqual(self.client.post('/api/tokens').status_code, 401)

    def test_bad_login(self):
        self.assertEqual(self.client.post('/api/tokens', auth=('test', 'bar')).status_code, 401)
