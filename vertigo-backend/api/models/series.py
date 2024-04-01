import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm
from datetime  import datetime
from slugify import slugify

from api.models.issue import Issue
from api.models.genre import Genre

from flask import current_app, url_for

from api.app import db
from api.helpers.thumbnail_processing import save_series_thumbnail
from api.models.updatable import Updateable
from api.models.associations import *


class Series(Updateable, db.Model):
    __tablename__ = 'series'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)

    publisher = sqla.Column(sqla.String(280))
    
    genre = sqla_orm.relationship('Genre', secondary=series_genre, 
                                  back_populates='series', lazy='dynamic')
    
    main_char = sqla.Column(sqla.String(280))
    writer = sqla.Column(sqla.String(280))
    artist = sqla.Column(sqla.String(280))

    inker = sqla.Column(sqla.String(280))
    penciller = sqla.Column(sqla.String(280))
    colorist = sqla.Column(sqla.String(280))
    letterer = sqla.Column(sqla.String(280))

    characters = sqla.Column(sqla.String(570))
    teams = sqla.Column(sqla.String(570))

    user_rating = sqla.Column(sqla.Float)

    editor = sqla.Column(sqla.String(280))
    description = sqla.Column(sqla.String(1250))

    issue = sqla_orm.relationship('Issue', back_populates='series',
                                  lazy='noload', cascade='all, delete-orphan')
    
    manga = sqla.Column(sqla.Integer)
    release_date = sqla.Column(sqla.DateTime)

    series_format = sqla.Column(sqla.String(100))
    issue_count = sqla.Column(sqla.Integer)

    read_count = sqla.Column(sqla.Integer)
    have_count = sqla.Column(sqla.Integer)

    dominant_color = sqla.Column(sqla.String(280))
    slug = sqla.Column(sqla.String(280))
    thumbnail = sqla.Column(sqla.String(280))
    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey("users.id"), index=True)

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
