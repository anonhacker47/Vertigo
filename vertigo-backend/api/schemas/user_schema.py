from marshmallow import validate, validates,\
    ValidationError, post_dump
from api import ma, db
from api.utils.auth import token_auth
from api.models.user import User

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
