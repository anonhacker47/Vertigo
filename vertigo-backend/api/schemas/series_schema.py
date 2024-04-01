from marshmallow import validate,\
     post_dump
from api import ma, db
from api.utils.auth import token_auth
from api.models.series import Series
from api.schemas.user_schema import UserSchema

class SeriesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Series
        include_fk = True
        ordered = True

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
    
    title = ma.auto_field(required=True, validate=validate.Length(
        min=1, max=280))
    publisher = ma.auto_field() 
    writer = ma.auto_field(validate=validate.Length(
        min=0, max=280))   
    artist = ma.auto_field(validate=validate.Length(
        min=0, max=280))

    inker = ma.auto_field(validate=validate.Length(
        min=0, max=280))   
    penciller = ma.auto_field(validate=validate.Length(
        min=0, max=280))   
    colorist = ma.auto_field(validate=validate.Length(
        min=0, max=280))   
    letterer = ma.auto_field(validate=validate.Length(
        min=0, max=280))

    characters = ma.auto_field(validate=validate.Length(
        min=0, max=570))
    
    teams = ma.auto_field(validate=validate.Length(
        min=0, max=570))   
    
    editor = ma.auto_field(validate=validate.Length(
        min=0, max=280))  
    
    description = ma.auto_field(validate=validate.Length(
        min=0, max=1250))  
    
    characters = ma.auto_field(validate=validate.Length(
        min=0, max=570))

    teams = ma.auto_field(validate=validate.Length(
        min=0, max=570))

    user_rating = ma.auto_field()

    main_char = ma.auto_field(validate=validate.Length(
        min=0, max=280)) 
    
    manga = ma.Integer(validate=validate.OneOf([0, 1]))

    release_date = ma.auto_field() 
        
    series_format = ma.auto_field(validate=validate.Length(
        min=1, max=100))
    
    issue_count = ma.auto_field() 
    read_count = ma.auto_field() 
    have_count = ma.auto_field() 
    
    genre =  ma.auto_field(validate=validate.Length(
        min=0, max=280))   
    
    dominant_color = ma.String()
    slug = ma.String()
    thumbnail = ma.String()
    timestamp = ma.auto_field(dump_only=True)
    user = ma.Nested(UserSchema, dump_only=True)

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        data['timestamp'] += 'Z'
        return data
