from time import time

import jwt
import sqlalchemy as sqla

from api.app import db

series_genre = sqla.Table('series_genre', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey('series.id'), primary_key=True),
    sqla.Column('genre_id', sqla.Integer, sqla.ForeignKey('genre.id'), primary_key=True)
)


