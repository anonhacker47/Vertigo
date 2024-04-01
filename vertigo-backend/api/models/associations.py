from time import time

import jwt
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

series_writer = sqla.Table('series_writer', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('writer_id', sqla.Integer, sqla.ForeignKey('writer.id'), primary_key=True)
)

series_artist = sqla.Table('series_artist', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('artist_id', sqla.Integer, sqla.ForeignKey('artist.id'), primary_key=True)
)

series_editor = sqla.Table('series_editor', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('editor_id', sqla.Integer, sqla.ForeignKey('editor.id'), primary_key=True)
)

series_inker = sqla.Table('series_inker', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('inker_id', sqla.Integer, sqla.ForeignKey('inker.id'), primary_key=True)
)

series_penciller = sqla.Table('series_penciller', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('penciller_id', sqla.Integer, sqla.ForeignKey('penciller.id'), primary_key=True)
)

series_colorist = sqla.Table('series_colorist', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('colorist_id', sqla.Integer, sqla.ForeignKey('colorist.id'), primary_key=True)
)

series_letterer = sqla.Table('series_letterer', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('letterer_id', sqla.Integer, sqla.ForeignKey('letterer.id'), primary_key=True)  
)

series_character = sqla.Table('series_character', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('character_id', sqla.Integer, sqla.ForeignKey('character.id'), primary_key=True)
)

series_team = sqla.Table('series_team', db.Model.metadata,
    sqla.Column('series_id', sqla.Integer, sqla.ForeignKey(SERIES_ID_FOREIGN_KEY), primary_key=True),
    sqla.Column('team_id', sqla.Integer, sqla.ForeignKey('team.id'), primary_key=True)
)

