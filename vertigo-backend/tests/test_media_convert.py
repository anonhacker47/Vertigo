import io
import os

from PIL import Image
from werkzeug.datastructures import FileStorage

from api import db, media
from api.media import convert
from api.media_convert import convert_media
from api.models.series import Series
from api.models.user import User
from tests.base_test_case import BaseTestCase


def image_bytes(size, fmt='PNG', mode='RGB', color=(200, 30, 30), frames=1):
    buf = io.BytesIO()
    img = Image.new(mode, size, color)
    if frames > 1:
        img.save(buf, fmt, save_all=True, append_images=[Image.new(mode, size, (30, 200, 30))], duration=100)
    else:
        img.save(buf, fmt)
    return buf.getvalue()


def upload(data, name='x.png'):
    return FileStorage(io.BytesIO(data), filename=name)


class StoreConvertsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))

    def stored(self, relpath):
        return Image.open(media.resolve(self.user.id, relpath))

    def test_large_uploads_become_webp_within_the_cap(self):
        relpath, _ = media.store(self.user.id, 'series/1', 'cover', upload(image_bytes((3000, 4500))))
        self.assertEqual(relpath, 'series/1/cover.webp')
        with self.stored(relpath) as img:
            self.assertEqual((img.format, img.size), ('WEBP', (1000, 1500)))

    def test_small_uploads_keep_their_size(self):
        relpath, _ = media.store(self.user.id, 'series/1', 'cover', upload(image_bytes((300, 450), 'JPEG'), 'x.jpg'))
        with self.stored(relpath) as img:
            self.assertEqual((img.format, img.size), ('WEBP', (300, 450)))

    def test_transparency_survives(self):
        relpath, _ = media.store(self.user.id, 'entities/publisher', '1',
                                 upload(image_bytes((40, 40), mode='RGBA', color=(0, 0, 0, 0))))
        with self.stored(relpath) as img:
            self.assertEqual(img.convert('RGBA').getpixel((5, 5))[3], 0)

    def test_animated_gifs_are_stored_as_they_are(self):
        relpath, _ = media.store(self.user.id, 'series/1', 'cover', upload(image_bytes((40, 40), 'GIF', frames=2), 'x.gif'))
        self.assertEqual(relpath, 'series/1/cover.gif')
        with self.stored(relpath) as img:
            self.assertTrue(img.is_animated)

    def test_pillow_encoder_is_used_without_cwebp(self):
        had = convert.CWEBP
        convert.CWEBP = None
        try:
            relpath, _ = media.store(self.user.id, 'series/1', 'cover', upload(image_bytes((1200, 600))))
        finally:
            convert.CWEBP = had
        with self.stored(relpath) as img:
            self.assertEqual((img.format, img.size), ('WEBP', (1000, 500)))

    def test_replacing_a_cover_removes_the_old_file(self):
        first, _ = media.store(self.user.id, 'series/1', 'cover', upload(image_bytes((40, 40), 'GIF', frames=2), 'x.gif'))
        second, _ = media.store(self.user.id, 'series/1', 'cover', upload(image_bytes((40, 40))), replace=first)
        self.assertEqual(second, 'series/1/cover.webp')
        self.assertIsNone(media.resolve(self.user.id, first))


class BackfillTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))
        media.init_user_dirs(self.user.id)

    def plant(self, relpath, data):
        full = os.path.join(media.user_root(self.user.id), relpath)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'wb') as fh:
            fh.write(data)
        return full

    def test_old_files_are_re_encoded_and_removed(self):
        series = Series(title='A', user=self.user)
        db.session.add(series)
        db.session.flush()
        old = self.plant(f'series/{series.id}/cover.jpeg', image_bytes((2000, 3000), 'JPEG'))
        series.thumbnail = f'series/{series.id}/cover.jpeg'
        self.user.profile_picture = 'avatar/avatar.png'
        avatar = self.plant('avatar/avatar.png', image_bytes((64, 64)))
        db.session.commit()
        stamp = series.thumbnail_updated

        summary = convert_media(log=lambda _line: None)

        self.assertEqual(summary['converted'], 2)
        self.assertEqual(series.thumbnail, f'series/{series.id}/cover.webp')
        self.assertEqual(self.user.profile_picture, 'avatar/avatar.webp')
        self.assertGreater(series.thumbnail_updated, stamp)
        with Image.open(media.resolve(self.user.id, series.thumbnail)) as img:
            self.assertEqual((img.format, img.size), ('WEBP', (1000, 1500)))
        self.assertFalse(os.path.exists(old))
        self.assertFalse(os.path.exists(avatar))
        self.assertEqual(convert_media(log=lambda _line: None)['converted'], 0)

    def test_dry_run_and_animated_images_change_nothing(self):
        series = Series(title='A', user=self.user)
        db.session.add(series)
        db.session.flush()
        old = self.plant(f'series/{series.id}/cover.jpeg', image_bytes((100, 150), 'JPEG'))
        series.thumbnail = f'series/{series.id}/cover.jpeg'
        gif = Series(title='B', user=self.user)
        db.session.add(gif)
        db.session.flush()
        self.plant(f'series/{gif.id}/cover.gif', image_bytes((40, 40), 'GIF', frames=2))
        gif.thumbnail = f'series/{gif.id}/cover.gif'
        db.session.commit()

        summary = convert_media(dry_run=True, log=lambda _line: None)
        self.assertEqual((summary['converted'], summary['skipped']), (1, 1))
        self.assertTrue(os.path.exists(old))
        self.assertEqual(series.thumbnail, f'series/{series.id}/cover.jpeg')

        convert_media(log=lambda _line: None)
        self.assertEqual(gif.thumbnail, f'series/{gif.id}/cover.gif')
