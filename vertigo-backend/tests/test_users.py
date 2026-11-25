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
        # another user's record is not served
        rv = self.client.get(f'/api/users/{user_id}')
        assert rv.status_code == 404

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

    def test_get_user(self):
        rv = self.client.get('/api/users/1')
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
        rv = self.client.put('/api/me', data={'username': 'test', 'email': 'test@example.com'})
        assert rv.status_code == 200
        assert rv.json['username'] == 'test'
        assert rv.json['email'] == 'test@example.com'

    def test_edit_me(self):
        rv = self.client.put('/api/me', data={'username': 'tester', 'preferred_currency': 'eur'})
        assert rv.status_code == 200
        assert rv.json['username'] == 'tester'
        assert rv.json['email'] == 'test@example.com'
        assert rv.json['preferred_currency'] == 'EUR'
        assert 'password' not in rv.json

    def test_edit_me_rejects_bad_values(self):
        other = User(username='other', email='other@example.com', password='foo')
        db.session.add(other)
        db.session.commit()
        for data in ({'username': 'other'}, {'username': '1x'}, {'email': 'other@example.com'},
                     {'email': 'nope'}, {'preferred_currency': 'euro'}):
            assert self.client.put('/api/me', data=data).status_code == 400, data

    def test_edit_password(self):
        rv = self.client.put('/api/me', data={'password': 'bar'})
        assert rv.status_code == 400
        rv = self.client.put('/api/me', data={'old_password': 'foo1', 'password': 'bar'})
        assert rv.status_code == 400
        rv = self.client.put('/api/me', data={'old_password': 'foo', 'password': 'bar'})
        assert rv.status_code == 200
        assert 'password' not in rv.json

        rv = self.client.post('/api/tokens', auth=('test@example.com', 'foo'))
        assert rv.status_code == 401
        rv = self.client.post('/api/tokens', auth=('test@example.com', 'bar'))
        assert rv.status_code == 200


class ShelfSettingsTests(BaseTestCase):
    def test_defaults(self):
        rv = self.client.get('/api/me/shelf')
        assert rv.status_code == 200
        assert rv.json == {'standees': None, 'order': 'publisher', 'show': 'all', 'publisher': None, 'finish': 'charcoal'}

    def test_rejects_an_unknown_order(self):
        rv = self.client.put('/api/me/shelf', json={'order': 'colour'})
        assert rv.status_code == 400

    def test_rejects_an_unknown_finish(self):
        rv = self.client.put('/api/me/shelf', json={'finish': 'oak'})
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
            'finish': 'white',
        })
        assert rv.status_code == 200
        assert rv.json == {'standees': [abe.id], 'order': 'unread', 'show': 'unread', 'publisher': dark_horse.id,
                           'finish': 'white'}
        rv = self.client.get('/api/me/shelf')
        assert rv.json['standees'] == [abe.id]
        assert rv.json['publisher'] == dark_horse.id
        rv = self.client.delete('/api/delete_all_data')
        assert rv.status_code == 200
        assert self.client.get('/api/me/shelf').json['standees'] is None
