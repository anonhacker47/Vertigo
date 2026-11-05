import io
import json
import os
import zipfile
from datetime import datetime

from openpyxl import load_workbook
from PIL import Image
from werkzeug.datastructures import FileStorage

from api import db, media
from api.models.issue import Issue
from api.models.series import Series
from api.models.series_entities import Character, Creator, Genre, Publisher
from api.models.user import User
from api.transfer import runs
from tests.base_test_case import BaseTestCase, TestConfig


class TransferConfig(TestConfig):
    TRANSFER_RUN_INLINE = True


def png_bytes(color):
    buf = io.BytesIO()
    Image.new('RGB', (8, 12), color).save(buf, 'PNG')
    return buf.getvalue()


def store_png(user_id, rel_dir, filename, color=(200, 30, 30)):
    relpath, _ = media.store(user_id, rel_dir, filename, FileStorage(io.BytesIO(png_bytes(color)), 'x.png'))
    return relpath


class TransferTestCase(BaseTestCase):
    config = TransferConfig

    def setUp(self):
        super().setUp()
        runs.reset()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))
        self.user_id = self.user.id
        media.init_user_dirs(self.user_id)

    # -- fixtures --------------------------------------------------------------------------

    def seed_collection(self):
        u = self.user
        dc = Publisher(title='DC Comics', user=u, metron_id='1', description='Big two')
        moore = Creator(title='Alan Moore', user=u, metron_id='7')
        hellblazer_char = Character(title='John Constantine', user=u)
        horror = Genre(title='Horror', user=u)
        db.session.add_all([dc, moore, hellblazer_char, horror])
        db.session.flush()
        dc.thumbnail = store_png(u.id, media.entity_dir('publisher'), str(dc.id), (10, 10, 200))

        hb = Series(title='Hellblazer', user=u, metron_id='77', metron_url='https://metron.cloud/series/hellblazer/',
                    notes='Keep the Ennis run', user_rating=4.5, series_format='Single issue',
                    description='Occult detective', release_date=datetime(1988, 1, 1),
                    timestamp=datetime(2025, 5, 1, 12, 0), dominant_color='#112233')
        hb.publisher = [dc]
        hb.creator = [moore]
        hb.character = [hellblazer_char]
        hb.genre = [horror]
        akira = Series(title='Akira', user=u, manga=True, timestamp=datetime(2025, 6, 1))
        db.session.add_all([hb, akira])
        db.session.flush()
        hb.thumbnail = store_png(u.id, media.series_dir(hb.id), 'cover')

        issues = [
            Issue(title='Original Sins', number=1, series=hb, user=u, is_owned=1, is_read=1,
                  bought_price=4.5, bought_date=datetime(2025, 5, 2), read_date=datetime(2025, 5, 3),
                  cover_date=datetime(1988, 1, 1), user_rating=5, notes='Signed', metron_id='1001',
                  description='The first one'),
            Issue(title='2', number=2, series=hb, user=u, is_owned=1, is_read=0, bought_price=3.0,
                  bought_date=datetime(2025, 5, 4)),
            Issue(title='3', number=3, series=hb, user=u, is_owned=0, is_read=0),
            Issue(title='1', number=1, series=akira, user=u, is_owned=1, is_read=1,
                  bought_date=datetime(2025, 6, 2), read_date=datetime(2025, 6, 3), bought_price=12.0),
            Issue(title='2', number=2, series=akira, user=u, is_owned=0, is_read=0),
        ]
        db.session.add_all(issues)
        db.session.flush()
        issues[0].thumbnail = store_png(u.id, media.issues_dir(hb.id), str(issues[0].id), (0, 200, 0))
        for s in (hb, akira):
            s.refresh_counts()
        u.profile_picture = store_png(u.id, media.AVATAR_DIR, 'avatar', (9, 9, 9))
        u.shelf_settings = {'standees': [hellblazer_char.id], 'order': 'unread', 'show': 'all', 'publisher': dc.id}
        db.session.commit()
        self.hb_id, self.akira_id = hb.id, akira.id
        self.constantine_id, self.dc_id = hellblazer_char.id, dc.id

    def me(self):
        """The test user, fetched again: a run closes the session and detaches ``self.user``."""
        return db.session.get(User, self.user_id)

    def series(self, title):
        return db.session.scalar(Series.select().where(Series.title == title, Series.user_id == self.user_id))

    def titles(self):
        return sorted(s.title for s in db.session.scalars(self.me().series_select()))

    def issues_of(self, series):
        return {i.number: i for i in db.session.scalars(series.issue_select())}

    def upload(self, url, filename, data, **fields):
        return self.client.post(url, data={'file': (io.BytesIO(data), filename), **fields},
                                content_type='multipart/form-data')

    def backup_zip(self):
        rv = self.client.get('/api/backup')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.mimetype, 'application/zip')
        data = rv.data
        rv.close()
        return data


class TestExport(TransferTestCase):
    def test_sheets_carry_notes_characters_format_dates_ratings_and_ids(self):
        self.seed_collection()
        rv = self.client.get('/api/export_data')
        self.assertEqual(rv.status_code, 200)
        wb = load_workbook(io.BytesIO(rv.data), data_only=True)
        self.assertEqual(wb.sheetnames, ['Series', 'Issues', 'Stats'])

        series_rows = list(wb['Series'].iter_rows(values_only=True))
        headers = list(series_rows[0])
        for column in ('Characters', 'Format', 'Manga', 'Notes', 'Rating', 'Metron ID'):
            self.assertIn(column, headers)
        by_title = {row[headers.index('Series Title')]: dict(zip(headers, row)) for row in series_rows[1:]}
        hb = by_title['Hellblazer']
        self.assertEqual(hb['Characters'], 'John Constantine')
        self.assertEqual(hb['Format'], 'Single issue')
        self.assertEqual(hb['Manga'], 'No')
        self.assertEqual(hb['Notes'], 'Keep the Ennis run')
        self.assertEqual(hb['Metron ID'], '77')
        self.assertEqual(hb['Owned Count'], '2 / 3')
        self.assertEqual(by_title['Akira']['Manga'], 'Yes')

        issue_rows = list(wb['Issues'].iter_rows(values_only=True))
        iheaders = list(issue_rows[0])
        for column in ('Issue Title', 'Cover Date', 'Rating', 'Notes', 'Metron ID'):
            self.assertIn(column, iheaders)
        first = dict(zip(iheaders, issue_rows[1]))
        self.assertEqual(first['Series Title'], 'Akira')  # sheets are ordered by title
        hb_first = dict(zip(iheaders, issue_rows[3]))
        self.assertEqual(hb_first['Issue Title'], 'Original Sins')
        self.assertEqual(hb_first['Cover Date'], datetime(1988, 1, 1))
        self.assertEqual(hb_first['Rating'], 5)
        self.assertEqual(hb_first['Metron ID'], '1001')
        # merged title cells: the second Hellblazer row has a blank title
        self.assertIsNone(dict(zip(iheaders, issue_rows[4]))['Series Title'])
        self.assertIsNone(dict(zip(iheaders, issue_rows[4]))['Issue Title'])  # "2" is not a custom title

    def test_an_empty_collection_still_exports(self):
        rv = self.client.get('/api/export_data')
        self.assertEqual(rv.status_code, 200)


class TestBackupAndRestore(TransferTestCase):
    def test_backup_holds_the_document_and_the_images(self):
        self.seed_collection()
        with zipfile.ZipFile(io.BytesIO(self.backup_zip())) as zf:
            names = set(zf.namelist())
            data = json.loads(zf.read('backup.json'))
        self.assertEqual(data['format'], 'vertigo-backup')
        self.assertEqual(data['version'], 1)
        self.assertEqual(data['user']['username'], 'test')
        self.assertEqual([s['title'] for s in data['series']], ['Hellblazer', 'Akira'])
        hb = data['series'][0]
        self.assertEqual(hb['metron_id'], '77')
        self.assertEqual(hb['publisher_ids'], [data['publishers'][0]['id']])
        self.assertEqual(hb['issues'][0]['is_owned'], True)
        self.assertEqual(hb['issues'][0]['bought_date'], '2025-05-02T00:00:00')
        self.assertIn(f"images/{hb['thumbnail']}", names)
        self.assertIn(f"images/{hb['issues'][0]['thumbnail']}", names)
        self.assertIn(f"images/{data['publishers'][0]['thumbnail']}", names)
        self.assertIn(f"images/{data['user']['profile_picture']}", names)
        self.assertEqual(data['user']['shelf_settings'],
                         {'standees': [self.constantine_id], 'order': 'unread', 'show': 'all', 'publisher': self.dc_id})

    def test_restore_into_an_empty_account_round_trips(self):
        self.seed_collection()
        archive = self.backup_zip()
        self.client.delete('/api/delete_all_data')
        self.user.preferred_currency = 'USD'
        self.user.profile_picture = None
        db.session.commit()
        self.assertIsNone(self.series('Hellblazer'))

        rv = self.upload('/api/restore', 'backup.zip', archive)
        self.assertEqual(rv.status_code, 202, rv.json)
        run = rv.json
        self.assertEqual(run['status'], 'done', run)
        self.assertEqual(run['summary']['series'], 2)
        self.assertEqual(run['summary']['issues'], 5)
        self.assertEqual(run['summary']['entities'], 4)
        self.assertEqual(run['summary']['images'], 4)
        self.assertEqual(run['done'], run['total'])

        rv = self.client.get(f"/api/transfer/runs/{run['id']}")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.json['status'], 'done')

        hb = self.series('Hellblazer')
        self.assertIsNotNone(hb)
        self.assertEqual(hb.metron_id, '77')
        self.assertEqual(hb.notes, 'Keep the Ennis run')
        self.assertEqual(hb.user_rating, 4.5)
        self.assertEqual(hb.series_format, 'Single issue')
        self.assertEqual(hb.timestamp, datetime(2025, 5, 1, 12, 0))
        self.assertEqual(hb.release_date, datetime(1988, 1, 1))
        self.assertEqual([p.title for p in hb.publisher], ['DC Comics'])
        self.assertEqual([c.title for c in hb.creator], ['Alan Moore'])
        self.assertEqual([c.title for c in hb.character], ['John Constantine'])
        self.assertEqual([g.title for g in hb.genre], ['Horror'])
        self.assertEqual((hb.issue_count, hb.owned_count, hb.read_count, hb.purchase_cost), (3, 2, 1, 7.5))
        self.assertEqual(hb.thumbnail, f'series/{hb.id}/cover.png')
        self.assertTrue(os.path.isfile(media.resolve(self.user_id, hb.thumbnail)))

        issues = self.issues_of(hb)
        first = issues[1]
        self.assertEqual(first.title, 'Original Sins')
        self.assertEqual((first.is_owned, first.is_read), (1, 1))
        self.assertEqual(first.bought_price, 4.5)
        self.assertEqual(first.bought_date, datetime(2025, 5, 2))
        self.assertEqual(first.read_date, datetime(2025, 5, 3))
        self.assertEqual(first.cover_date, datetime(1988, 1, 1))
        self.assertEqual(first.user_rating, 5)
        self.assertEqual(first.notes, 'Signed')
        self.assertEqual(first.metron_id, '1001')
        self.assertEqual(first.thumbnail, f'series/{hb.id}/issues/{first.id}.png')
        self.assertTrue(os.path.isfile(media.resolve(self.user_id, first.thumbnail)))
        self.assertIsNone(issues[3].thumbnail)

        akira = self.series('Akira')
        self.assertTrue(akira.manga)
        self.assertEqual(akira.issue_count, 2)

        publisher = db.session.scalar(Publisher.select().where(Publisher.user_id == self.user_id))
        self.assertEqual(publisher.description, 'Big two')
        self.assertEqual(publisher.thumbnail, f'entities/publisher/{publisher.id}.png')
        self.assertTrue(os.path.isfile(media.resolve(self.user_id, publisher.thumbnail)))

        self.assertEqual(self.me().profile_picture, 'avatar/avatar.png')

    def test_a_full_account_needs_a_mode(self):
        self.seed_collection()
        archive = self.backup_zip()
        rv = self.upload('/api/restore', 'backup.zip', archive)
        self.assertEqual(rv.status_code, 409)
        self.assertEqual(rv.json['error'], 'account_not_empty')
        self.assertEqual(rv.json['backup']['series'], 2)
        self.assertEqual(rv.json['account']['series'], 2)
        self.assertEqual(self.titles(), ['Akira', 'Hellblazer'])

    def test_merge_adds_only_what_is_missing(self):
        self.seed_collection()
        archive = self.backup_zip()
        # lose Akira and Hellblazer #2, and give #1 a new rating the backup does not know about
        self.client.delete(f'/api/series/{self.akira_id}')
        hb = self.series('Hellblazer')
        issues = self.issues_of(hb)
        db.session.delete(issues[2])
        issues[1].user_rating = 2
        hb.refresh_counts()
        db.session.commit()

        rv = self.upload('/api/restore', 'backup.zip', archive, mode='merge')
        self.assertEqual(rv.status_code, 202, rv.json)
        summary = rv.json['summary']
        self.assertEqual(rv.json['status'], 'done', rv.json)
        self.assertEqual((summary['series'], summary['series_matched']), (1, 1))
        self.assertEqual((summary['issues'], summary['issues_skipped']), (3, 2))
        self.assertEqual((summary['entities'], summary['entities_matched']), (0, 4))
        self.assertNotIn('safety_backup', summary)

        self.assertEqual(self.titles(), ['Akira', 'Hellblazer'])
        hb = self.series('Hellblazer')
        issues = self.issues_of(hb)
        self.assertEqual(sorted(issues), [1, 2, 3])
        self.assertEqual(issues[1].user_rating, 2)        # kept, not overwritten
        self.assertEqual(issues[2].bought_price, 3.0)     # restored
        self.assertEqual(hb.owned_count, 2)
        self.assertEqual(len(db.session.scalars(Publisher.select()).all()), 1)
        self.assertEqual(self.me().shelf_settings['standees'], [self.constantine_id])   # kept

    def test_replace_wipes_first(self):
        self.seed_collection()
        archive = self.backup_zip()
        extra = Series(title='Preacher', user=self.user)
        db.session.add(extra)
        db.session.commit()

        rv = self.upload('/api/restore', 'backup.zip', archive, mode='replace')
        self.assertEqual(rv.status_code, 202, rv.json)
        self.assertEqual(rv.json['status'], 'done', rv.json)
        self.assertEqual(self.titles(), ['Akira', 'Hellblazer'])
        self.assertEqual(self.series('Hellblazer').owned_count, 2)

        # the replaced collection was saved on the server first
        folder = os.path.join(self.data_dir, 'backups')
        saved = rv.json['summary']['safety_backup']
        self.assertEqual(os.listdir(folder), [saved])
        with zipfile.ZipFile(os.path.join(folder, saved)) as zf:
            copy = json.loads(zf.read('backup.json'))
        self.assertIn('Preacher', [s['title'] for s in copy['series']])

    def test_merge_keeps_same_titled_series_with_other_metron_ids_apart(self):
        self.seed_collection()
        archive = self.backup_zip()
        self.series('Hellblazer').metron_id = '999'   # now a different Metron series than the backup's 77
        self.series('Akira').metron_id = '555'        # linked here, unlinked in the backup
        db.session.commit()

        rv = self.upload('/api/restore', 'backup.zip', archive, mode='merge')
        self.assertEqual(rv.json['status'], 'done', rv.json)
        titles = self.titles()
        self.assertEqual(titles.count('Hellblazer'), 2)   # different id: a second series
        self.assertEqual(titles.count('Akira'), 1)        # backup had no id: merged by title
        self.assertEqual(rv.json['summary']['series'], 1)

    def test_shelf_settings_follow_the_restored_ids(self):
        self.seed_collection()
        archive = self.backup_zip()
        self.client.delete('/api/delete_all_data')
        self.assertIsNone(self.me().shelf_settings)
        # another user's rows push the next ids past the backed-up ones
        other = User(username='other', email='other@example.com', password='foo')
        db.session.add(other)
        db.session.flush()
        db.session.add_all([Character(title='Filler', user=other), Publisher(title='Filler', user=other)])
        db.session.commit()

        rv = self.upload('/api/restore', 'backup.zip', archive)
        self.assertEqual(rv.json['status'], 'done', rv.json)
        constantine = db.session.scalar(Character.select().where(Character.user_id == self.user_id))
        dc = db.session.scalar(Publisher.select().where(Publisher.user_id == self.user_id))
        self.assertNotEqual(constantine.id, self.constantine_id)
        self.assertEqual(self.me().shelf_settings,
                         {'standees': [constantine.id], 'order': 'unread', 'show': 'all', 'publisher': dc.id})

    def test_a_failed_run_keeps_the_counts_it_reached(self):
        self.seed_collection()
        archive = self.backup_zip()
        self.client.delete('/api/delete_all_data')
        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            data = json.loads(zf.read('backup.json'))
        data['series'][1]['issues'][0]['bought_price'] = 'free'   # fails in plan, before anything is written
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('backup.json', json.dumps(data))
        rv = self.upload('/api/restore', 'broken.zip', buf.getvalue())
        self.assertEqual(rv.status_code, 400)
        self.assertIn('bought_price', rv.json['description'])
        self.assertEqual(self.titles(), [])   # nothing was touched

    def test_refuses_files_that_are_not_backups(self):
        rv = self.upload('/api/restore', 'notes.txt', b'hello')
        self.assertEqual(rv.status_code, 400)
        self.assertIn('not a Vertigo backup', rv.json['description'])

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('readme.txt', 'nope')
        rv = self.upload('/api/restore', 'other.zip', buf.getvalue())
        self.assertEqual(rv.status_code, 400)
        self.assertIn('backup.json', rv.json['description'])

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('backup.json', json.dumps({'format': 'vertigo-backup', 'version': 99, 'series': []}))
        rv = self.upload('/api/restore', 'future.zip', buf.getvalue())
        self.assertEqual(rv.status_code, 400)
        self.assertIn('newer Vertigo', rv.json['description'])

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('backup.json', json.dumps({'format': 'vertigo-backup', 'version': 1,
                                                   'series': [{'title': 'X', 'issues': [{'number': 'one'}]}]}))
        rv = self.upload('/api/restore', 'broken.zip', buf.getvalue())
        self.assertEqual(rv.status_code, 400)
        self.assertIn('not a whole number', rv.json['description'])
        self.assertIsNone(self.series('X'))

    def test_run_lookup_is_per_user(self):
        rv = self.client.get('/api/transfer/runs/nope')
        self.assertEqual(rv.status_code, 404)
