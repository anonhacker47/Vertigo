import io

from PIL import Image
from werkzeug.datastructures import FileStorage

from api import db, media
from api.models.user import User
from tests.base_test_case import BaseTestCase


def png():
    buf = io.BytesIO()
    Image.new('RGB', (8, 8), (10, 200, 30)).save(buf, 'PNG')
    return buf.getvalue()


class AvatarTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))

    def test_me_carries_no_avatar_without_a_picture(self):
        rv = self.client.get('/api/me')
        self.assertIsNone(rv.json['avatar'])
        rv = self.client.get(f'/api/users/{self.user.id}/avatar')
        self.assertEqual(rv.json, media.NOIMAGE)

    def test_avatar_is_a_plain_image_url(self):
        relpath, _ = media.store(self.user.id, media.AVATAR_DIR, 'avatar', FileStorage(io.BytesIO(png()), 'a.png'))
        self.user.profile_picture = relpath
        db.session.commit()
        url = self.client.get('/api/me').json['avatar']
        self.assertIn(f'/api/users/{self.user.id}/avatar?t=', url)
        rv = self.client.get(url.split('localhost:5000', 1)[1])
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.mimetype, 'image/webp')

    def test_unknown_user_is_404(self):
        self.assertEqual(self.client.get('/api/users/999/avatar').status_code, 404)
