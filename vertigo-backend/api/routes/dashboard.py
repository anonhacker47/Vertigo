from flask import jsonify
from sqlalchemy import desc,func


from flask import Blueprint, abort
from apifairy import authenticate, other_responses

from api import db
from api.models.series import Series
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


field_options = ['publisher', 'genre', 'main_char', 'writer', 'artist', 'editor']

@dashboard.route('/users/<int:user_id>/<string:field>/<string:type>/count', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def user_field_count(user_id, field, type):
    """Retrieve count of series by field for a user"""
    if field not in field_options or type not in ['issue', 'series']:
        abort(400, description='Invalid field or type')

    if type == 'issue':
        field_count = (
            db.session.query(getattr(Series, field), func.count(Issue.id).label('value'))
            .filter(Series.id == Issue.series_id)
            .filter_by(user_id=user_id)
            .group_by(getattr(Series, field))
            .order_by(desc('value'))
            .limit(7)
            .all()
        )

    else:
        field_count = (
            db.session.query(getattr(Series, field), func.count(Series.id).label('value'))
            .filter_by(user_id=user_id)
            .group_by(getattr(Series, field))
            .order_by(desc('value'))
            .limit(7)
            .all()
        )

    field_count_json = [{'value': item[1], 'name': item[0]} for item in field_count]
    return jsonify(field_count_json)




