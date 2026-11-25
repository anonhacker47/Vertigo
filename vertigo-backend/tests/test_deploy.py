import gzip
import os

from api import db, media
from api.models.series import Series
from api.models.user import User
from tests.base_test_case import BaseTestCase, TestConfigWithAuth


class SameOriginConfig(TestConfigWithAuth):
    USE_CORS = False


class RefreshCookieTests(BaseTestCase):
    config = SameOriginConfig

    def cookie(self, scheme):
        rv = self.client.post('/api/tokens', auth=('test', 'foo'),
                              base_url=f'{scheme}://localhost:5000')
        self.assertEqual(rv.status_code, 200)
        return rv.headers['Set-Cookie']

    def test_secure_over_https(self):
        self.assertIn('Secure', self.cookie('https'))

    def test_not_secure_over_http(self):
        cookie = self.cookie('http')
        self.assertNotIn('Secure', cookie)
        self.assertIn('SameSite=Strict', cookie)


class CoverCacheTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        user = db.session.scalar(User.select().where(User.username == 'test'))
        relpath = 'series/1/cover.webp'
        series = Series(title='A', user=user, thumbnail=relpath)
        db.session.add(series)
        db.session.commit()
        path = os.path.join(media.user_root(user.id), relpath)
        os.makedirs(os.path.dirname(path))
        with open(path, 'wb') as f:
            f.write(b'cover')
        self.url = f'/api/series/image/{series.id}'

    def test_versioned_url_is_immutable(self):
        rv = self.client.get(self.url + '?t=1')
        self.assertEqual(rv.headers['Content-Type'], 'image/webp')
        cache = rv.headers['Cache-Control']
        self.assertIn('max-age=31536000', cache)
        self.assertIn('immutable', cache)
        rv.close()

    def test_plain_url_revalidates(self):
        rv = self.client.get(self.url)
        self.assertIn('no-cache', rv.headers['Cache-Control'])
        rv.close()


class FrontendFilesTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        root = os.path.join(self.data_dir, 'wwwroot')
        os.makedirs(os.path.join(root, 'static'))
        self.app.config['WWWROOT'] = root
        self.script = b'console.log("vertigo");' * 20
        self.write(root, 'index.html', b'<html></html>')
        self.write(root, 'static/app.js', self.script)
        self.write(root, 'static/app.js.gz', gzip.compress(self.script))

    def write(self, root, name, data):
        with open(os.path.join(root, name), 'wb') as f:
            f.write(data)

    def test_static_uses_the_gzip_sibling(self):
        rv = self.client.get('/static/app.js', headers={'Accept-Encoding': 'gzip'})
        self.assertEqual(rv.headers['Content-Encoding'], 'gzip')
        self.assertIn('javascript', rv.headers['Content-Type'])
        self.assertIn('immutable', rv.headers['Cache-Control'])
        self.assertEqual(gzip.decompress(rv.data), self.script)
        rv.close()

    def test_static_plain_without_accept_encoding(self):
        rv = self.client.get('/static/app.js')
        self.assertNotIn('Content-Encoding', rv.headers)
        self.assertEqual(rv.data, self.script)
        rv.close()

    def test_client_routes_get_an_uncached_index(self):
        rv = self.client.get('/series/42')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data, b'<html></html>')
        self.assertIn('no-cache', rv.headers['Cache-Control'])
        rv.close()

    def test_missing_static_file_is_404(self):
        self.assertEqual(self.client.get('/static/nope.js').status_code, 404)

    def test_large_json_is_gzipped(self):
        user = db.session.scalar(User.select().where(User.username == 'test'))
        db.session.add_all([Series(title=f'Series {i}', user=user) for i in range(40)])
        db.session.commit()
        rv = self.client.get('/api/sync/full', headers={'Accept-Encoding': 'gzip'})
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers.get('Content-Encoding'), 'gzip')
        self.assertTrue(gzip.decompress(rv.data).startswith(b'{'))
