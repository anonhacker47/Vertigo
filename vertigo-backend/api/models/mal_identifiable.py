import sqlalchemy as sqla

class MalIdentifiable:
    mal_id = sqla.Column(sqla.Integer)
    mal_url = sqla.Column(sqla.String(280))
