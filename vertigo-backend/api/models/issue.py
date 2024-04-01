import sqlalchemy as sqla
from sqlalchemy import orm as sqla_orm
from datetime  import datetime
from slugify import slugify

from flask import url_for

from api.app import db
from api.models.updatable import Updateable

class Issue(Updateable, db.Model):
    __tablename__ = 'issue'

    id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(280), nullable=False)
    number = sqla.Column(sqla.Integer)
    summary = sqla.Column(sqla.String(570))

    slug = sqla.Column(sqla.String(280))

    read_whole = sqla.Column(sqla.Integer)
    have_whole = sqla.Column(sqla.Integer)

    bought_date = sqla.Column(sqla.DateTime)
    read_date = sqla.Column(sqla.DateTime)

    timestamp = sqla.Column(sqla.DateTime, index=True, default=datetime.utcnow,
                            nullable=False)

    series_id = sqla.Column(
        sqla.Integer, sqla.ForeignKey("series.id"), index=True)

    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey("users.id"), index=True)

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
