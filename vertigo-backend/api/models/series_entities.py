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
        if not 'slug' in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '{}'.format(self.title)

    @property
    def url(self):
        return url_for('publisher.get', id=self.id)


class Writer(Updateable, db.Model):
    __tablename__ = 'writer'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_writer, back_populates='writer',
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
        return url_for('writer.get', id=self.id)

class Editor(Updateable, db.Model):
    __tablename__ = 'editor'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_editor, back_populates='editor',
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
        return url_for('editor.get', id=self.id)

class Artist(Updateable, db.Model):
    __tablename__ = 'artist'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_artist, back_populates='artist',
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
        return url_for('Artist.get', id=self.id)

class Colorist(Updateable, db.Model):
    __tablename__ = 'colorist'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_colorist, back_populates='colorist',
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
        return url_for('Colorist.get', id=self.id)

class Inker(Updateable, db.Model):
    __tablename__ = 'inker'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_inker, back_populates='inker',
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
        return url_for('Inker.get', id=self.id)

class Character(Updateable, db.Model):
    __tablename__ = 'character'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_character, back_populates='character',
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
        return url_for('character.get', id=self.id)

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

class Penciller(Updateable, db.Model):

    __tablename__ = 'penciller'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_penciller, back_populates='penciller',
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
        return url_for('penciller.get', id=self.id)

class Letterer(Updateable, db.Model):
    __tablename__ = 'letterer'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_letterer, back_populates='letterer',
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
        return url_for('letterer.get', id=self.id)

class Team(Updateable, db.Model):
    __tablename__ = 'team'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=associations.series_team, back_populates='team',
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
        return url_for('team.get', id=self.id)
