import sqlalchemy as sqla
import jwt
from time import time
from sqlalchemy import orm as sqla_orm

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from flask import current_app, url_for

from api.app import db
from api.models.updatable import Updateable
from api.models.token import Token
from api.models.series import Series
from api.models.issue import Issue
from api.models import series_entities


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
    
    publisher = sqla_orm.relationship('Publisher', back_populates='user',
                                  lazy='noload')
    
    genre = sqla_orm.relationship('Genre', back_populates='user',
                                  lazy='noload')    

    creator = sqla_orm.relationship('Creator', back_populates='user',
                                  lazy='noload')

    character = sqla_orm.relationship('Character', back_populates='user',
                                  lazy='noload')
            
    preferred_currency = sqla.Column(sqla.String(3), default='USD')
    profile_picture = sqla.Column(sqla.String(280))
    metron_api_token = sqla.Column(sqla.String(255))
    shelf_settings = sqla.Column(sqla.JSON)

    def series_select(self):
        return Series.select().where(sqla_orm.with_parent(self, User.series))

    def issue_select(self):
        return Issue.select().where(sqla_orm.with_parent(self, User.issue))

    def publisher_select(self):
        return series_entities.Publisher.select().where(sqla_orm.with_parent(self, User.publisher))

    def creator_select(self):
        return series_entities.Creator.select().where(sqla_orm.with_parent(self, User.creator))

    def character_select(self):
        return series_entities.Character.select().where(sqla_orm.with_parent(self, User.character))

    def __repr__(self):  # pragma: no cover
        return '<User {}>'.format(self.username)

    @property
    def url(self):
        return url_for('users.get', id=self.id)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self):
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(access_token_jwt, refresh_token=None):
        token = Token.from_jwt(access_token_jwt)
        if token:
            if token.access_expiration > datetime.utcnow():
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
