from marshmallow import validate, post_dump
from api import ma
from api.models.issue import Issue

from api.schemas.user_schema import UserSchema
from api.schemas.series_schema import SeriesSchema

class IssueSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Issue
        include_fk = True
        ordered = True

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
        
    title = ma.auto_field(validate=validate.Length(
        min=1, max=280))
    
    number = ma.auto_field() 
    
    read_whole = ma.auto_field() 
    have_whole = ma.auto_field() 

    bought_date = ma.auto_field() 
    read_date = ma.auto_field()

    slug = ma.String()

    timestamp = ma.auto_field(dump_only=True)

    series = ma.Nested(SeriesSchema, dump_only=True)
    
    user = ma.Nested(UserSchema, dump_only=True)

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        data['timestamp'] += 'Z'
        return data
