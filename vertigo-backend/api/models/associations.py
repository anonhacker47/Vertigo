import sqlalchemy as sqla
from api.app import db

SERIES_ID_FOREIGN_KEY = 'series.id'

series_publisher = sqla.Table('series_publisher', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('publisher_id', sqla.Integer, sqla.ForeignKey('publisher.id'), primary_key=True)
)

series_genre = sqla.Table('series_genre', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('genre_id', sqla.Integer, sqla.ForeignKey('genre.id'), primary_key=True)
)

series_creator = sqla.Table('series_creator', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('creator_id', sqla.Integer, sqla.ForeignKey('creator.id'), primary_key=True)
)

series_character = sqla.Table('series_character', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('character_id', sqla.Integer, sqla.ForeignKey('character.id'), primary_key=True)
)
