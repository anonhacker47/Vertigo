import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm
from datetime  import datetime
from slugify import slugify

import api.models.associations as associations 
from flask import current_app, url_for

from api.app import db
from api.models.updatable import Updateable

class Publisher(Updateable, db.Model):
    __tablename__ = 'publisher'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_publisher, back_populates='publisher',
                                   lazy='noload')

    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '{}'.format(self.title)

    @property
    def url(self):
        return url_for('publisher.get', id=self.id)

class MainCharacter(Updateable, db.Model):
    __tablename__ = 'main_character'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_main_character, back_populates='main_character',
                                   lazy='noload')

    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '{}'.format(self.title)

    @property
    def url(self):
        return url_for('main_character.get', id=self.id)

class Creator(Updateable, db.Model):
    __tablename__ = 'creator'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_creator, back_populates='creator',
                                   lazy='noload')

    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '{}'.format(self.title)

    @property
    def url(self):
        return url_for('creator.get', id=self.id)

class Genre(Updateable, db.Model):
    __tablename__ = 'genre'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_genre, back_populates='genre',
                                   lazy='noload')

    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '{}'.format(self.title)

    @property
    def url(self):
        return url_for('genre.get', id=self.id)
