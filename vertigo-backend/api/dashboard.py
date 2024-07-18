import os
from pstats import SortKey
from flask import current_app, jsonify
import sqlite3
from sqlalchemy import desc,func


from flask import Blueprint, abort, request, send_file, send_from_directory
from apifairy import authenticate, body, response, other_responses

from api import db
from api.models import User, Series, Issue
from api.schemas import SeriesSchema, EmptySchema, IssueSchema

from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import DateTimePaginationSchema
from api.helpers import save_series_thumbnail,delete_series_thumbnail


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
        .filter(Series.have_count == Series.books_count)
        .count()
    )
    return jsonify({'totalSeriesCount': series_count, 'collectedSeriesCount': completed_series_count})



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
    return jsonify({'totalIssueCount': issue_count, 'collectedIssueCount': completed_issue_count})



@dashboard.route('/users/<int:user_id>/series/read', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def user_read_series(user_id):
    """Retrieve number of series completely read by a user"""
    read_series_count = (
        db.session.query(Series)
        .filter_by(user_id=user_id)
        .filter(Series.have_count == Series.books_count)
        .count()
    )
    return jsonify({'readSeriesCount': read_series_count})


@dashboard.route('/users/<int:user_id>/issues/read', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def user_read_issues(user_id):
    """Retrieve number of issues completely read by a user"""
    read_issue_count = (
        db.session.query(Issue)
        .filter_by(user_id=user_id)
        .filter(Issue.read_whole == 1)
        .count()
    )
    return jsonify({'readIssueCount': read_issue_count})



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




