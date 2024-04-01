from marshmallow import validate,\
     post_dump
from api import ma, db
from api.utils.auth import token_auth
from api.models.genre import Genre

class GenreSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Genre
        include_fk = True
        ordered = True

    id = ma.auto_field(dump_only=True)
    
    title = ma.auto_field(required=True, validate=validate.Length(
        min=1, max=280))
    
    description = ma.auto_field(validate=validate.Length(
        min=0, max=1250))

    timestamp = ma.auto_field(dump_only=True)

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        if 'timestamp' in data:
            data['timestamp'] += 'Z'
        return data