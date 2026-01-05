from marshmallow import post_load, validate, post_dump, fields, EXCLUDE
from api import ma
from api.models.series import Series
from api.schemas.user_schema import UserSchema

class EntityDumpSchema(ma.Schema):
    id = ma.Int()
    title = ma.String()
    slug = ma.String()

class SeriesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Series
        include_fk = True
        ordered = True
        unknown = EXCLUDE  # Ignore unknown fields
        exclude = ["user"]

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
    
    title = ma.auto_field(required=True, validate=validate.Length(min=1, max=280))
    publisher = ma.List(ma.String(validate=validate.Length(min=0, max=280)), allow_none=True)
    creator = ma.List(ma.String(validate=validate.Length(min=0, max=280)), allow_none=True)
      
    character = ma.List(ma.String(validate=validate.Length(min=0, max=280), allow_none=True))
        
    description = ma.auto_field(validate=validate.Length(min=0, max=3000))

    user_rating = ma.auto_field()

    manga = ma.Integer(validate=validate.OneOf([0, 1]), allow_none=True)

    release_date = ma.auto_field() 
        
    series_format = ma.auto_field(validate=validate.Length(min=1, max=100), allow_none=True)

    genre = ma.List(ma.Nested(EntityDumpSchema), dump_only=True)
    creator = ma.List(ma.Nested(EntityDumpSchema), dump_only=True)
    character = ma.List(ma.Nested(EntityDumpSchema), dump_only=True)
    publisher = ma.List(ma.Nested(EntityDumpSchema), dump_only=True)
    
    issue_count = ma.auto_field()
    read_count = ma.auto_field()
    owned_count = ma.auto_field()
    purchase_cost = ma.auto_field()
    
    genre = ma.List(ma.String, allow_none=True)
    
    dominant_color = ma.String()
    slug = ma.String()
    thumbnail = ma.String()
    timestamp = ma.auto_field(dump_only=True)
    user = ma.Nested(UserSchema, dump_only=True)

    metron_id = ma.String(allow_none=True)
    metron_url = ma.String(allow_none=True)

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        if 'timestamp' in data:
            data['timestamp'] += 'Z'
        if 'publisher' in data and isinstance(data['publisher'], list):
            data['publisher'] = data['publisher'][0] if data['publisher'] else None
        return data
