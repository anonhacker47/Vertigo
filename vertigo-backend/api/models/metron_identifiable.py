import sqlalchemy as sqla

class MetronIdentifiable:
    metron_id = sqla.Column(sqla.String)
    metron_url = sqla.Column(sqla.String(280))