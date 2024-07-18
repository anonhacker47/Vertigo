from datetime import datetime, timedelta
from hashlib import md5
import uuid
from PIL import Image
import secrets
from time import time
import requests
import re

from flask import current_app, url_for
import jwt
import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
import shutil

from api.app import db
from api.helpers import save_series_thumbnail


class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


followers = sqla.Table(
    'followers',
    db.Model.metadata,
    sqla.Column('follower_id', sqla.Integer, sqla.ForeignKey('users.id')),
    sqla.Column('followed_id', sqla.Integer, sqla.ForeignKey('users.id'))
)


class Token(db.Model):
    __tablename__ = 'tokens'

    id = sqla.Column(sqla.Integer, primary_key=True)
    access_token = sqla.Column(sqla.String(64), nullable=False, index=True)
    access_expiration = sqla.Column(sqla.DateTime, nullable=False)
    refresh_token = sqla.Column(sqla.String(64), nullable=False, index=True)
    refresh_expiration = sqla.Column(sqla.DateTime, nullable=False)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey('users.id'),
                          index=True)

    user = sqla_orm.relationship('User', back_populates='tokens')

    @property
    def access_token_jwt(self):
        return jwt.encode({'token': self.access_token},
                          current_app.config['SECRET_KEY'],
                          algorithm='HS256')

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() + \
            timedelta(minutes=current_app.config['ACCESS_TOKEN_MINUTES'])
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = datetime.utcnow() + \
            timedelta(days=current_app.config['REFRESH_TOKEN_DAYS'])

    def expire(self):
        self.access_expiration = datetime.utcnow()
        self.refresh_expiration = datetime.utcnow()

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        db.session.execute(Token.delete().where(
            Token.refresh_expiration < yesterday))

    @staticmethod
    def from_jwt(access_token_jwt):
        access_token = None
        try:
            access_token = jwt.decode(access_token_jwt,
                                      current_app.config['SECRET_KEY'],
                                      algorithms=['HS256'])['token']
            return db.session.scalar(Token.select().filter_by(
                access_token=access_token))
        except jwt.PyJWTError:
            pass


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
    


class Series(Updateable, db.Model):
    __tablename__ = 'series'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    publisher = sqla.Column(sqla.String(280))
    genre = sqla.Column(sqla.String(280))
    main_char = sqla.Column(sqla.String(280))
    writer = sqla.Column(sqla.String(280))
    artist = sqla.Column(sqla.String(280))
    editor = sqla.Column(sqla.String(280))
    summary = sqla.Column(sqla.String(570))

    issue = sqla_orm.relationship('Issue', back_populates='series',
                                  lazy='noload', cascade='all, delete-orphan')

    series_format = sqla.Column(sqla.String(100))
    books_count = sqla.Column(sqla.Integer)

    read_count = sqla.Column(sqla.Integer)
    have_count = sqla.Column(sqla.Integer)

    dominant_color = sqla.Column(sqla.String(280))
    slug = sqla.Column(sqla.String(280))
    thumbnail = sqla.Column(sqla.String(280))
    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey(User.id), index=True)

    user = sqla_orm.relationship('User', back_populates='series')


    def issue_select(self):
        return Issue.select().where(sqla_orm.with_parent(self, Series.issue))

    def __init__(self, *args, **kwargs):
        if not 'slug' in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))

            url = kwargs.get('thumbnail', '')

        thumbnail_filename, dominant_color = save_series_thumbnail(url, kwargs['title'])
        kwargs['dominant_color'] = dominant_color
        kwargs['thumbnail'] = thumbnail_filename
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<Series {}>'.format(self.title, self.thumbnail, self.slug)

    @property
    def url(self):
        return url_for('series.get', id=self.id)


class Issue(Updateable, db.Model):
    __tablename__ = 'issue'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    slug = sqla.Column(sqla.String(280))

    read_whole = sqla.Column(sqla.Integer)
    have_whole = sqla.Column(sqla.Integer)

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)

    series_id = sqla.Column(
        sqla.Integer, sqla.ForeignKey(Series.id), index=True)

    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey(User.id), index=True)

    user = sqla_orm.relationship('User', back_populates='issue')

    series = sqla_orm.relationship('Series', back_populates='issue')

    def __init__(self, *args, **kwargs):
        if not 'slug' in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))
        

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<Issue {}>'.format(self.slug)

    @property
    def url(self):
        return url_for('issue.get', id=self.id)
