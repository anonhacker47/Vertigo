from flask import jsonify
from sqlalchemy import desc,func


from flask import Blueprint, abort
from apifairy import authenticate, other_responses

from api import db
from api.models.series import Series
import api.models.series_entities as series_entities
import api.models.associations as associations
from api.models.issue import Issue
from api.schemas.series_schema import SeriesSchema 
from api.schemas.issue_schema import IssueSchema


from api.utils.auth import token_auth


dashboard = Blueprint('dashboard', __name__)

series_schema = SeriesSchema()
multi_series_schema = SeriesSchema(many=True)
update_series_schema = SeriesSchema(partial=True)

issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True)
update_issue_schema = IssueSchema(partial=True)


@dashboard.route('/users/<int:user_id>/series/stats', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def user_series_stats(user_id):
    """Retrieve series count stats from a user"""
    series_count = db.session.query(Series).filter_by(user_id=user_id).count()
    completed_series_count = (
        db.session.query(Series)
        .filter_by(user_id=user_id)
        .filter(Series.have_count == Series.issue_count)
        .count()
    )
    
    read_series_count = (
        db.session.query(Series)
        .filter_by(user_id=user_id)
        .filter(Series.read_count == Series.issue_count)
        .count()
    )    
    return jsonify({'totalSeriesCount': series_count, 'collectedSeriesCount': completed_series_count,'readSeriesCount': read_series_count})



@dashboard.route('/users/<int:user_id>/issues/stats', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def user_issues_stats(user_id):
    """Retrieve issues count stats from a user"""
    issue_count = db.session.query(Issue).filter_by(user_id=user_id).count()
    completed_issue_count = (
        db.session.query(Issue)
        .filter_by(user_id=user_id)
        .filter(Issue.have_whole == 1)
        .count()
    )
    read_issue_count = (
        db.session.query(Issue)
        .filter_by(user_id=user_id)
        .filter(Issue.read_whole == 1)
        .count()
    )
    return jsonify({'totalIssueCount': issue_count, 'collectedIssueCount': completed_issue_count,'readIssueCount': read_issue_count})


@dashboard.route('/users/<int:user_id>/<string:field>/<string:type>/count', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def user_field_count(user_id, field, type):
    """Retrieve count of series by field for a user"""
    
    field_mappings = {
        'publisher': {
            'model': series_entities.Publisher,
            'table': associations.series_publisher,
            'column': 'publisher_id'
        },
        'genre': {
            'model': series_entities.Genre,
            'table': associations.series_genre,
            'column': 'genre_id'
        },
        'writer': {
            'model': series_entities.Writer,
            'table': associations.series_writer,
            'column': 'writer_id'
        },
        'artist': {
            'model': series_entities.Artist,
            'table': associations.series_artist,
            'column': 'artist_id'
        },
        'editor': {
            'model': series_entities.Editor,
            'table': associations.series_editor,
            'column': 'editor_id'
        },
        'inker': {
            'model': series_entities.Inker,
            'table': associations.series_inker,
            'column': 'inker_id'
        },
        'penciller': {
            'model': series_entities.Penciller,
            'table': associations.series_penciller,
            'column': 'penciller_id'
        },
        'colorist': {
            'model': series_entities.Colorist,
            'table': associations.series_colorist,
            'column': 'colorist_id'
        },
        'letterer': {
            'model': series_entities.Letterer,
            'table': associations.series_letterer,
            'column': 'letterer_id'
        },
        'character': {
            'model': series_entities.Character,
            'table': associations.series_character,
            'column': 'character_id'
        },
        'team': {
            'model': series_entities.Team,
            'table': associations.series_team,
            'column': 'team_id'
        }
    }


    if field not in field_mappings:
        abort(400, description='Field not supported')

    field_info = field_mappings[field]
    field_model = field_info['model']
    field_table = field_info['table']
    field_column = field_info['column']

    if type == 'issue':

        field_count = (
            db.session.query(field_model.title, func.count(Issue.id).label('value'))
            .join(field_table, field_model.id == field_table.c[field_column])
            .join(Series, field_table.c.series_id == Series.id)
            .filter(Series.id == Issue.series_id)
            .filter(Series.user_id == user_id)
            .group_by(field_model.title)
            .order_by(desc('value'))
            .limit(7)
            .all()
        )
    else:
        
        field_count = (
            db.session.query(field_model.title, func.count(Series.id).label('value'))
            .join(field_table, field_model.id == field_table.c[field_column])
            .join(Series, field_table.c.series_id == Series.id)
            .filter(Series.user_id == user_id)
            .group_by(field_model.title)
            .order_by(desc('value'))
            .limit(7)
            .all()
        )

    field_count_json = [{'value': item[1], 'name': item[0]} for item in field_count]
    return jsonify(field_count_json)




