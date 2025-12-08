from marshmallow import validate, post_dump
from sqlalchemy import func
from api import ma, db
from api.models.series_entities import Genre
from api.utils.auth import token_auth
from api.models import associations
from api.models.series import Series

class CharacterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Genre
        include_fk = True
        ordered = True

    id = ma.auto_field(dump_only=True,)
    
    title = ma.auto_field(required=True, validate=validate.Length(
        min=1, max=280))
    
    description = ma.auto_field(validate=validate.Length(
        min=0, max=1250))
    
    thumbnail = ma.String()

    
    slug = ma.String()
    timestamp = ma.auto_field(dump_only=True)

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        if 'timestamp' in data:
            data['timestamp'] += 'Z'
        return data
    
class CharacterDetailSchema(CharacterSchema):
    series_count = ma.Method("get_series_count")

    def get_series_count(self, obj):
        user = token_auth.current_user()

        stmt = (
            db.session.query(func.count())
            .select_from(associations.series_character)
            .join(Series, Series.id == associations.series_character.c.series_id)
            .filter(
                associations.series_character.c.character_id == obj.id,
                Series.user_id == user.id
            )
        )
        return stmt.scalar()