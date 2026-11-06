from api import db
from api.models.series_entities import Character, Publisher
from api.models.user import User
from tests.base_test_case import BaseTestCase


class UserTests(BaseTestCase):
    def test_create_user(self):
        rv = self.client.post('/api/users', json={
            'username': 'user',
            'email': 'user@example.com',
            'password': 'dog'
        })
        assert rv.status_code == 201
        user_id = rv.json['id']
        rv = self.client.post('/api/users', json={
            'username': 'user',
            'email': 'user2@example.com',
            'password': 'dog'
        })
        assert rv.status_code == 400
        rv = self.client.post('/api/users', json={
            'username': 'user2',
            'email': 'user@example.com',
            'password': 'dog'
        })
        assert rv.status_code == 400
        rv = self.client.get(f'/api/users/{user_id}')
        assert rv.status_code == 200
        assert rv.json['username'] == 'user'
        assert rv.json['email'] == 'user@example.com'

    def test_create_invalid_user(self):
        rv = self.client.post('/api/users', json={
            'username': '1user',
            'email': 'user@example.com',
            'password': 'dog'
        })
        assert rv.status_code == 400
        rv = self.client.post('/api/users', json={
            'username': '',
            'email': 'user@example.com',
            'password': 'dog'
        })
        assert rv.status_code == 400

    def test_get_users(self):
        rv = self.client.get('/api/users')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 1
        assert rv.json['data'][0]['username'] == 'test'
        assert rv.json['data'][0]['email'] == 'test@example.com'
        assert 'password' not in rv.json['data'][0]

    def test_get_user(self):
        rv = self.client.get('/api/users/1')
        assert rv.status_code == 200
        assert rv.json['id'] == 1
        assert rv.json['username'] == 'test'
        assert rv.json['email'] == 'test@example.com'
        assert 'password' not in rv.json
        rv = self.client.get('/api/users/test')
        assert rv.status_code == 200
        assert rv.json['id'] == 1
        assert rv.json['username'] == 'test'
        assert rv.json['email'] == 'test@example.com'
        assert 'password' not in rv.json

    def test_get_me(self):
        rv = self.client.get('/api/me')
        assert rv.status_code == 200
        assert rv.json['username'] == 'test'
        assert rv.json['email'] == 'test@example.com'
        assert 'password' not in rv.json

    def test_edit_user_no_changes(self):
        rv = self.client.get('/api/me')
        assert rv.status_code == 200
        rv2 = self.client.put('/api/me', json={
            'username': rv.json['username'],
            'email': rv.json['email'],
            'about_me': rv.json['about_me'],
        })
        assert rv2.status_code == 200
        assert rv2.json['username'] == rv.json['username']
        assert rv2.json['email'] == rv.json['email']
        assert rv2.json['about_me'] == rv.json['about_me']

    def test_edit_me(self):
        rv = self.client.put('/api/me', json={
            'about_me': 'I am testing',
        })
        assert rv.status_code == 200
        assert rv.json['username'] == 'test'
        assert rv.json['email'] == 'test@example.com'
        assert rv.json['about_me'] == 'I am testing'
        assert 'password' not in rv.json

    def test_edit_password(self):
        rv = self.client.put('/api/me', json={
            'password': 'bar',
        })
        assert rv.status_code == 400
        rv = self.client.put('/api/me', json={
            'old_password': 'foo1',
            'password': 'bar',
        })
        assert rv.status_code == 400
        rv = self.client.put('/api/me', json={
            'old_password': 'foo',
            'password': 'bar',
        })
        assert rv.status_code == 200
        assert rv.json['username'] == 'test'
        assert rv.json['email'] == 'test@example.com'
        assert 'password' not in rv.json

        rv = self.client.post('/api/tokens', auth=('test@example.com', 'foo'))
        assert rv.status_code == 401
        rv = self.client.post('/api/tokens', auth=('test@example.com', 'bar'))
        assert rv.status_code == 200

    def test_follow_unfollow(self):
        rv = self.client.get('/api/me/following')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 0
        assert rv.json['data'] == []

        rv = self.client.get('/api/me/followers')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 0
        assert rv.json['data'] == []

        rv = self.client.post('/api/users', json={
            'username': 'susan',
            'email': 'susan@example.com',
            'password': 'dog',
        })
        assert rv.status_code == 201
        id = rv.json['id']

        rv = self.client.get(f'/api/me/following/{id}')
        assert rv.status_code == 404

        rv = self.client.post(f'/api/me/following/{id}')
        assert rv.status_code == 204

        rv = self.client.get(f'/api/me/following/{id}')
        assert rv.status_code == 204

        rv = self.client.post(f'/api/me/following/{id}')
        assert rv.status_code == 409

        rv = self.client.get('/api/me/following')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 1
        assert rv.json['data'][0]['username'] == 'susan'

        rv = self.client.get('/api/me/followers')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 0

        rv = self.client.get('/api/me/following')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 1
        assert rv.json['data'][0]['username'] == 'susan'

        rv = self.client.get('/api/me/followers')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 0

        rv = self.client.get('/api/users/2/following')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 0

        rv = self.client.get('/api/users/2/followers')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 1
        assert rv.json['data'][0]['username'] == 'test'

        rv = self.client.delete(f'/api/me/following/{id}')
        assert rv.status_code == 204

        rv = self.client.delete(f'/api/me/following/{id}')
        assert rv.status_code == 409

        rv = self.client.get('/api/me/following')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 0
        assert rv.json['data'] == []


class ShelfSettingsTests(BaseTestCase):
    def test_defaults(self):
        rv = self.client.get('/api/me/shelf')
        assert rv.status_code == 200
        assert rv.json == {'standees': None, 'order': 'publisher', 'show': 'unread', 'publisher': None}

    def test_rejects_an_unknown_order(self):
        rv = self.client.put('/api/me/shelf', json={'order': 'colour'})
        assert rv.status_code == 400

    def test_rejects_too_many_standees(self):
        rv = self.client.put('/api/me/shelf', json={'standees': [1, 2, 3]})
        assert rv.status_code == 400

    def test_rejects_a_strangers_character(self):
        other = User(username='other', email='other@example.com', password='foo')
        db.session.add(other)
        db.session.commit()
        theirs = Character(title='Rorschach', user_id=other.id)
        db.session.add(theirs)
        db.session.commit()
        rv = self.client.put('/api/me/shelf', json={'standees': [theirs.id]})
        assert rv.status_code == 400

    def test_round_trip(self):
        me = db.session.get(User, 1)
        abe = Character(title='Abe Sapien', user_id=me.id)
        dark_horse = Publisher(title='Dark Horse', user_id=me.id)
        db.session.add_all([abe, dark_horse])
        db.session.commit()
        rv = self.client.put('/api/me/shelf', json={
            'standees': [abe.id, abe.id], 'order': 'unread', 'show': 'unread', 'publisher': dark_horse.id,
        })
        assert rv.status_code == 200
        assert rv.json == {'standees': [abe.id], 'order': 'unread', 'show': 'unread', 'publisher': dark_horse.id}
        rv = self.client.get('/api/me/shelf')
        assert rv.json['standees'] == [abe.id]
        assert rv.json['publisher'] == dark_horse.id
        rv = self.client.delete('/api/delete_all_data')
        assert rv.status_code == 200
        assert self.client.get('/api/me/shelf').json['standees'] is None
