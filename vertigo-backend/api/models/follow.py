
from time import time

import jwt
import sqlalchemy as sqla

from api.app import db

followers = sqla.Table(
    'followers',
    db.Model.metadata,
    sqla.Column('follower_id', sqla.Integer, sqla.ForeignKey('users.id')),
    sqla.Column('followed_id', sqla.Integer, sqla.ForeignKey('users.id'))
)