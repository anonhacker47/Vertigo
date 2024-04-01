import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm
from datetime  import datetime
from slugify import slugify

from api.models.associations import series_artist
from flask import current_app, url_for

from api.app import db
from api.models.updatable import Updateable

class Artist(Updateable, db.Model):
    __tablename__ = 'artist'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    description = sqla.Column(sqla.String(1250))

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    
    series = sqla_orm.relationship('Series', secondary=series_artist, back_populates='artists',
                                   lazy='noload')

    def __init__(self, *args, **kwargs):
        if not 'slug' in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<Artist {}>'.format(self.title)

    @property
    def url(self):
        return url_for('artist.get', id=self.id)
