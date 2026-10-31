from api import db
from api.jobs import registry
from api.models.user import User
from tests.base_test_case import BaseTestCase


def inline(func, *args):
    """A queue that runs the task on the spot."""
    func(*args)
    return True


def parked(func, *args):
    """A queue that accepts the task and never gets round to it."""
    return True


def full(func, *args):
    return False


def ok():
    pass


def boom():
    raise ValueError('boom')


class TestJobRegistry(BaseTestCase):
    def setUp(self):
        super().setUp()
        registry.reset()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))

    def test_a_waiting_job_is_listed(self):
        job = registry.submit(parked, 'cover', 'Cover for Batman #1', self.user.id, ok)
        self.assertEqual(job.status, 'queued')
        self.assertEqual([j.id for j in registry.for_user(self.user.id)], [job.id])

    def test_a_finished_job_is_gone_however_it_went(self):
        registry.submit(inline, 'cover', 'fine', self.user.id, ok)
        with self.assertRaises(ValueError):
            registry.submit(inline, 'enrich', 'broken', self.user.id, boom)
        self.assertEqual(registry.for_user(self.user.id), [])

    def test_a_full_queue_never_lists_the_job(self):
        self.assertIsNone(registry.submit(full, 'collage', 'Rebuild the cover collage', self.user.id, ok))
        self.assertEqual(registry.for_user(self.user.id), [])

    def test_running_jobs_come_before_waiting_ones(self):
        seen = []

        def peek():
            seen.append([j.status for j in registry.for_user(self.user.id)])

        waiting = registry.submit(parked, 'cover', 'later', self.user.id, ok)
        registry.submit(inline, 'cover', 'now', self.user.id, peek)
        self.assertEqual(seen, [['running', 'queued']])
        self.assertEqual([j.id for j in registry.for_user(self.user.id)], [waiting.id])


class TestJobRoutes(BaseTestCase):
    def setUp(self):
        super().setUp()
        registry.reset()
        self.user = db.session.scalar(User.select().where(User.username == 'test'))

    def test_lists_only_the_users_pending_jobs(self):
        registry.submit(parked, 'cover', 'mine', self.user.id, ok)
        registry.submit(parked, 'cover', 'theirs', self.user.id + 1, ok)
        registry.submit(inline, 'cover', 'done already', self.user.id, ok)
        rv = self.client.get('/api/jobs')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual([j['label'] for j in rv.json['jobs']], ['mine'])
        self.assertEqual(rv.json['jobs'][0]['status'], 'queued')
