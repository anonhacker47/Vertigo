from api.models.user import User
from tests.base_test_case import BaseTestCase


class UserModelTests(BaseTestCase):
    def test_password_is_hashed_and_unreadable(self):
        u = User(username='susan', password='cat')
        self.assertFalse(u.verify_password('dog'))
        self.assertTrue(u.verify_password('cat'))
        self.assertNotEqual(u.password_hash, 'cat')
        with self.assertRaises(AttributeError):
            u.password
