from marshmallow import validate, post_dump
from api import ma
from api.models.issue import Issue

from api.schemas.user_schema import UserSchema
from api.schemas.series_schema import SeriesSchema, SlimSeriesSchema

class IssueSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Issue
        include_fk = True
        ordered = True
        exclude = (["user"])

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
        
    title = ma.auto_field(validate=validate.Length(
        min=1, max=280))
    
    number = ma.auto_field()
    cover_date = ma.auto_field()

    description = ma.auto_field(validate=validate.Length(max=570))

    notes = ma.auto_field(validate=validate.Length(
        max=3000))
    
    user_rating = ma.auto_field()
    
    is_read = ma.Boolean()
    is_owned = ma.Boolean() 

    bought_price= ma.auto_field() 
    bought_date = ma.auto_field() 
    read_date = ma.auto_field()

    slug = ma.String()

    # Relative path of the issue's own cover (see api/media); set only through
    # PUT /series/issues/<id>/cover. Null means "fall back to the series cover".
    thumbnail = ma.String(dump_only=True)

    timestamp = ma.auto_field(dump_only=True)
    last_updated = ma.auto_field(dump_only=True)

    series = ma.Nested(SeriesSchema, dump_only=True)
    series_id = ma.auto_field(dump_only=True)
    
    user = ma.Nested(UserSchema, dump_only=True)
    user_id = ma.auto_field(dump_only=True)

    metron_id = ma.Integer(allow_none=True)
    metron_url = ma.String(allow_none=True)
    @post_dump
    def fix_datetimes(self, data, **kwargs):
        data['timestamp'] += 'Z'
        return data


class BulkIssueIdsSchema(ma.Schema):
    """Which issues of the series a bulk call acts on."""
    class Meta:
        ordered = True

    ids = ma.List(ma.Integer(), required=True, validate=validate.Length(min=1, max=500))


class BulkIssueUpdateSchema(BulkIssueIdsSchema):
    """Fields set on every listed issue; anything omitted is left as it is."""
    is_owned = ma.Boolean()
    is_read = ma.Boolean()
    bought_date = ma.DateTime(allow_none=True)
    read_date = ma.DateTime(allow_none=True)
    bought_price = ma.Float(allow_none=True)


class SlimIssueSchema(IssueSchema):
    class Meta:
        model = Issue
        exclude = ("series",)


class LibraryIssueSchema(IssueSchema):
    class Meta(IssueSchema.Meta):
        pass

    series = ma.Nested(SlimSeriesSchema, dump_only=True)
