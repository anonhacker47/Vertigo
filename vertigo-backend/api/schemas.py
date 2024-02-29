from email.policy import default
from marshmallow import validate, validates, validates_schema, \
    ValidationError, post_dump
from api import ma, db
from api.auth import token_auth
from api.models import User, Series, Issue

paginated_schema_cache = {}


class EmptySchema(ma.Schema):
    pass


class DateTimePaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    after = ma.DateTime(load_only=True)
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('offset') is not None and data.get('after') is not None:
            raise ValidationError('Cannot specify both offset and after')


class StringPaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    after = ma.String(load_only=True)
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('offset') is not None and data.get('after') is not None:
            raise ValidationError('Cannot specify both offset and after')


def PaginatedCollection(schema, pagination_schema=StringPaginationSchema):
    if schema in paginated_schema_cache:
        return paginated_schema_cache[schema]

    class PaginatedSchema(ma.Schema):
        class Meta:
            ordered = True

        pagination = ma.Nested(pagination_schema)
        data = ma.Nested(schema, many=True)

    PaginatedSchema.__name__ = 'Paginated{}'.format(schema.__class__.__name__)
    paginated_schema_cache[schema] = PaginatedSchema
    return PaginatedSchema


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
    username = ma.auto_field(required=True,
                             validate=validate.Length(min=3, max=64))
    email = ma.auto_field(required=True, validate=[validate.Length(max=120),
                                                   validate.Email()])
    password = ma.String(required=True, load_only=True,
                         validate=validate.Length(min=3))
    avatar_url = ma.String(dump_only=True)
    first_seen = ma.auto_field(dump_only=True)
    series_url = ma.URLFor('series.user_all', values={'id': '<id>'},
                          dump_only=True)

    @validates('username')
    def validate_username(self, value):
        if not value[0].isalpha():
            raise ValidationError('Username must start with a letter')
        user = token_auth.current_user()
        old_username = user.username if user else None
        if value != old_username and \
                db.session.scalar(User.select().filter_by(username=value)):
            raise ValidationError('Use a different username.')

    @validates('email')
    def validate_email(self, value):
        user = token_auth.current_user()
        old_email = user.email if user else None
        if value != old_email and \
                db.session.scalar(User.select().filter_by(email=value)):
            raise ValidationError('Use a different email.')

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        if 'timestamp' in data:
            data['timestamp'] += 'Z'
        return data


class UpdateUserSchema(UserSchema):
    old_password = ma.String(load_only=True, validate=validate.Length(min=3))

    @validates('old_password')
    def validate_old_password(self, value):
        if not token_auth.current_user().verify_password(value):
            raise ValidationError('Password is incorrect')


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
    
    editor = ma.auto_field(validate=validate.Length(
        min=0, max=280))  
    
    summary = ma.auto_field(validate=validate.Length(
        min=0, max=570))  
    
    genre = ma.auto_field(validate=validate.Length(
        min=0, max=280)) 
    
    main_char = ma.auto_field(validate=validate.Length(
        min=0, max=280)) 
    
    
    series_format = ma.auto_field(validate=validate.Length(
        min=1, max=100))
    books_count = ma.auto_field() 
    read_count = ma.auto_field() 
    have_count = ma.auto_field() 
    
    
    dominant_color = ma.String()
    slug = ma.String()
    thumbnail = ma.String()
    timestamp = ma.auto_field(dump_only=True)
    user = ma.Nested(UserSchema, dump_only=True)

    
    @post_dump
    def fix_datetimes(self, data, **kwargs):
        data['timestamp'] += 'Z'
        return data

class IssueSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Issue
        include_fk = True
        ordered = True

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
        
    title = ma.auto_field(validate=validate.Length(
        min=1, max=280))

    read_whole = ma.auto_field() 
    have_whole = ma.auto_field() 
        
    slug = ma.String()

    timestamp = ma.auto_field(dump_only=True)

    series = ma.Nested(SeriesSchema, dump_only=True)
    
    user = ma.Nested(UserSchema, dump_only=True)

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        data['timestamp'] += 'Z'
        return data

class TokenSchema(ma.Schema):
    class Meta:
        ordered = True

    access_token = ma.String(required=True)
    refresh_token = ma.String()


class PasswordResetRequestSchema(ma.Schema):
    class Meta:
        ordered = True

    email = ma.String(required=True, validate=[validate.Length(max=120),
                                               validate.Email()])


class PasswordResetSchema(ma.Schema):
    class Meta:
        ordered = True

    token = ma.String(required=True)
    new_password = ma.String(required=True, validate=validate.Length(min=3))
