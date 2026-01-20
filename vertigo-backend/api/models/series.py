import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm
from datetime  import datetime, timezone
from slugify import slugify

from api.models.issue import Issue

from flask import current_app, url_for

from api.app import db
from api.helpers.thumbnail_processing import save_thumbnail
from api.models.syncable import Syncable
class Series(Updateable, MetronIdentifiable, Syncable, db.Model):
    __tablename__ = 'series'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)

    publisher = sqla_orm.relationship('Publisher', secondary=associations.series_publisher,
                                   back_populates='series', lazy='dynamic')
    
    
    genre = sqla_orm.relationship('Genre', secondary=associations.series_genre, 
                                  back_populates='series', lazy='dynamic')
    

    creator = sqla_orm.relationship('Creator', secondary=associations.series_creator,
                                   back_populates='series', lazy='dynamic')
    
    character = sqla_orm.relationship('Character', secondary=associations.series_character,
                                   back_populates='series', lazy='dynamic')

    user_rating = sqla.Column(sqla.Float)
    
    description = sqla.Column(sqla.String(3000))

    issue = sqla_orm.relationship('Issue', back_populates='series',
                                  lazy='noload', cascade='all, delete-orphan')
    
    manga = sqla.Column(sqla.Boolean, default=False)
    release_date = sqla.Column(sqla.DateTime)
    
    purchase_cost = sqla.Column(sqla.Float)

    series_format = sqla.Column(sqla.String(100))
    issue_count = sqla.Column(sqla.Integer)

    read_count = sqla.Column(sqla.Integer)
    owned_count = sqla.Column(sqla.Integer)


    dominant_color = sqla.Column(sqla.String(280))
    slug = sqla.Column(sqla.String(280))
    thumbnail = sqla.Column(sqla.String(280))
    
    timestamp = sqla.Column(sqla.DateTime, index=True, default=lambda: datetime.now(timezone.utc), nullable=False)

    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey("users.id"), index=True)

    user = sqla_orm.relationship('User', back_populates='series')

    def issue_select(self):
        return Issue.select().where(sqla_orm.with_parent(self, Series.issue))

    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<Series {}>'.format(self.title)

    @property
    def url(self):
        return url_for('series.get', id=self.id)
