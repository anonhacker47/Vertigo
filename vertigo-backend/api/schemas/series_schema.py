from marshmallow import post_load, validate, post_dump
from api import ma
from api.models.series import Series
from api.schemas.user_schema import UserSchema
from api.schemas.genre_schema import GenreSchema

class SeriesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Series
        include_fk = True
        ordered = True

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
    
    title = ma.auto_field(required=True, validate=validate.Length(
        min=1, max=280))
    publisher = ma.List(ma.String(validate=validate.Length(
        min=0, max=280))) 
    writer = ma.List(ma.String(validate=validate.Length(
        min=0, max=280)))
    artist = ma.List(ma.String(validate=validate.Length(
        min=0, max=280)))

    inker = ma.List(ma.String(validate=validate.Length(
        min=0, max=280)))  
    penciller = ma.List(ma.String(validate=validate.Length(
        min=0, max=280)))  
    colorist = ma.List(ma.String(validate=validate.Length(
        min=0, max=280)))  
    letterer = ma.List(ma.String(validate=validate.Length(
        min=0, max=280)))

    character = ma.List(ma.String(validate=validate.Length(
        min=0, max=280)))
      
    main_char = ma.String(validate=validate.Length(
        min=0, max=280))
    
    editor = ma.List(ma.String(validate=validate.Length(
        min=0, max=280))) 
    
    description = ma.auto_field(validate=validate.Length(
        min=0, max=1250))  

    team = ma.List(ma.String(validate=validate.Length(
        min=0, max=280)))

    user_rating = ma.auto_field()

    main_char_id = ma.auto_field()
    main_char_type = ma.String(validate=validate.OneOf(['character', 'team']))
    
    manga = ma.Integer(validate=validate.OneOf([0, 1]))

    release_date = ma.auto_field() 
        
    series_format = ma.auto_field(validate=validate.Length(
        min=1, max=100))
    
    issue_count = ma.auto_field() 
    read_count = ma.auto_field() 
    have_count = ma.auto_field() 
    
    genre = ma.List(ma.String)
    
    dominant_color = ma.String()
    slug = ma.String()
    thumbnail = ma.String()
    timestamp = ma.auto_field(dump_only=True)
    user = ma.Nested(UserSchema, dump_only=True)

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        if 'timestamp' in data:
            data['timestamp'] += 'Z'
        return data
    
    # @post_load
    # def process_genre(self, data, **kwargs):
    #     # Check if genre was passed as a string or a nested schema
    #     if isinstance(data.get('genre'), list):
    #         # If genre was passed as a string, create or get the genre object
    #         genre_title = data['genre'][0]
    #         genre = create_or_get_genre(genre_title)
    #         data['genre'] = genre
    #         print(genre)
    #     # If genre was passed as a nested schema, it's already processed
    #     return data
