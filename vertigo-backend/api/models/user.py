import sqlalchemy as sqla
import jwt
from time import time
from sqlalchemy import orm as sqla_orm

from datetime import datetime, timedelta
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash

from flask import current_app, url_for

from api.app import db
from api.models.updatable import Updateable
from api.models.token import Token
from api.models.series import Series


followers = sqla.Table(
    'followers',
    db.Model.metadata,
    sqla.Column('follower_id', sqla.Integer, sqla.ForeignKey('users.id')),
    sqla.Column('followed_id', sqla.Integer, sqla.ForeignKey('users.id'))
)


class User(Updateable, db.Model):
    __tablename__ = 'users'

    id = sqla.Column(sqla.Integer, primary_key=True)
    username = sqla.Column(sqla.String(64), index=True, unique=True,
                           nullable=False)
    email = sqla.Column(sqla.String(120), index=True, unique=True,
                        nullable=False)
    password_hash = sqla.Column(sqla.String(128))
    first_seen = sqla.Column(sqla.DateTime, default=datetime.utcnow)

    tokens = sqla_orm.relationship('Token', back_populates='user',
                                   lazy='noload')
    series = sqla_orm.relationship('Series', back_populates='user',
                                   lazy='noload')
    issue = sqla_orm.relationship('Issue', back_populates='user',
                                  lazy='noload')

    following = sqla_orm.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers', lazy='noload')
    followers = sqla_orm.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following', lazy='noload')

    def series_select(self):
        return Series.select().where(sqla_orm.with_parent(self, User.series))

    def covers_select(id):
        return Series.select().where(Series.id == id)
    
    def following_select(self):
        return User.select().where(sqla_orm.with_parent(self, User.following))

    def followers_select(self):
        return User.select().where(sqla_orm.with_parent(self, User.followers))

    def followed_series_select(self):
        return Series.select().join(
            followers, (followers.c.followed_id == Series.user_id),
            isouter=True).group_by(Series.id).filter(
                sqla.or_(Series.user == self,
                         followers.c.follower_id == self.id))

    def __repr__(self):  # pragma: no cover
        return '<User {}>'.format(self.username)

    @property
    def url(self):
        return url_for('users.get', id=self.id)

    @property
    def avatar_url(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()

    def generate_auth_token(self):
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(access_token_jwt, refresh_token=None):
        token = Token.from_jwt(access_token_jwt)
        if token:
            if token.access_expiration > datetime.utcnow():
                token.user.ping()
                db.session.commit()
                return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token_jwt):
        token = Token.from_jwt(access_token_jwt)
        if token and token.refresh_token == refresh_token:
            if token.refresh_expiration > datetime.utcnow():
                return token

            # someone tried to refresh with an expired token
            # revoke all tokens from this user as a precaution
            token.user.revoke_all()
            db.session.commit()

    def revoke_all(self):
        db.session.execute(Token.delete().where(Token.user == self))

    def generate_reset_token(self):
        return jwt.encode(
            {
                'exp': time() + current_app.config['RESET_TOKEN_MINUTES'] * 60,
                'reset_email': self.email,
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(reset_token):
        try:
            data = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return
        return db.session.scalar(User.select().filter_by(
            email=data['reset_email']))

    def follow(self, user):
        if not self.is_following(user):
            db.session.execute(followers.insert().values(
                follower_id=self.id, followed_id=user.id))

    def unfollow(self, user):
        if self.is_following(user):
            db.session.execute(followers.delete().where(
                followers.c.follower_id == self.id,
                followers.c.followed_id == user.id))

    def is_following(self, user):
        return db.session.scalars(User.select().where(
            User.id == self.id, User.following.contains(
                user))).one_or_none() is not None
    
