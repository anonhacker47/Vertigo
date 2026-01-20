import time
from datetime import datetime, timezone
from api import db
from api.models.series import Series
from api.models.issue import Issue
from api.models.user import User
from api.models.deleted_record import DeletedRecord
from tests.base_test_case import BaseTestCase

class TestSync(BaseTestCase):
    def test_syncable_timestamps(self):
        user = db.session.scalar(db.select(User).where(User.username == 'test'))
        
        series = Series(title='Test Series', user=user)
        db.session.add(series)
        db.session.commit()
        
        first_updated = series.last_updated
        self.assertIsNotNone(first_updated)
        
        time.sleep(0.1)
        
        series.description = 'Updated description'
        db.session.commit()
        
        second_updated = series.last_updated
        self.assertGreater(second_updated, first_updated)

    def test_sync_endpoint(self):
        user = db.session.scalar(db.select(User).where(User.username == 'test'))
        
        s1 = Series(title='S1', user=user)
        s2 = Series(title='S2', user=user)
        db.session.add_all([s1, s2])
        db.session.commit()
        
        # Test full sync
        rv = self.client.get('/api/sync')
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertEqual(len(data['series']), 2)
        
        # Test since
        t1 = s1.last_updated
        time.sleep(0.1)
        s2.description = 'update'
        db.session.commit()
        
        rv = self.client.get(f'/api/sync?since={t1.isoformat()}')
        data = rv.get_json()
        self.assertEqual(len(data['series']), 1)
        self.assertEqual(data['series'][0]['id'], s2.id)

    def test_deletion_logging_sync(self):
        user = db.session.scalar(db.select(User).where(User.username == 'test'))
        
        s1 = Series(title='To be deleted', user=user)
        db.session.add(s1)
        db.session.commit()
        
        s1_id = s1.id
        
        # Hard delete via route
        self.client.delete(f'/api/series/{s1_id}')
        
        # Verify it's gone from main table
        self.assertIsNone(db.session.get(Series, s1_id))
        
        # Verify it's in DeletedRecord
        deleted = db.session.scalar(
            db.select(DeletedRecord).where(
                DeletedRecord.table_name == 'series',
                DeletedRecord.object_id == s1_id
            )
        )
        self.assertIsNotNone(deleted)
        self.assertEqual(deleted.user_id, user.id)
        
        # Check sync endpoint
        rv = self.client.get('/api/sync')
        data = rv.get_json()
        self.assertEqual(len(data['series']), 0)
        self.assertIn(s1_id, data['deleted']['series'])
