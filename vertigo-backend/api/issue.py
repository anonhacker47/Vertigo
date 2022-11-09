import os
from pstats import SortKey
from flask import current_app

from flask import Blueprint, abort, request, send_file, send_from_directory
from apifairy import authenticate, body, response, other_responses

from api import db
from api.models import User,Series,Issue
from api.schemas import IssueSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import DateTimePaginationSchema


issues = Blueprint('issue', __name__)
issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True)
update_issue_schema = IssueSchema(partial=True)

@issues.route('/series/<int:series_id>/issues', methods=['POST'])
@authenticate(token_auth)
@body(issue_schema)
@response(issue_schema, 201)
def new(args,series_id):
    """Create a new issue"""
    user = token_auth.current_user()
    series = db.session.get(Series, series_id)
    issue = Issue(user=user,series=series, **args)
    db.session.add(issue)
    db.session.commit()
    return issue

@issues.route('/series/issues/<int:id>/', methods=['GET'])
@authenticate(token_auth)
@response(issue_schema)
@other_responses({404: 'Series not found'})
def get(id):
    """Retrieve an issue by id"""
    return db.session.get(Issue, id) or abort(404)


@issues.route('/series/issues/', methods=['GET'])
@authenticate(token_auth)
@paginated_response(issues_schema, order_by=Issue.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all issues"""
    return Issue.select()


@issues.route('/series/<int:id>/issues', methods=['GET'])
@authenticate(token_auth)
@paginated_response(issues_schema, order_by=Issue.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
@other_responses({404: 'User not found'})
def series_all(id):
    """Retrieve all issues from a series"""
    series = db.session.get(Series, id) or abort(404)
    return series.issue_select()


# @series.route('/series/<int:id>', methods=['PUT'])
# @authenticate(token_auth)
# @body(update_series_schema)
# @response(series_schema)
# @other_responses({403: 'Not allowed to edit this series',
#                   404: 'Series not found'})
# def put(data, id):
#     """Edit a series"""
#     series = db.session.get(Series, id) or abort(404)
#     if series.user != token_auth.current_user():
#         abort(403)
#     series.update(data)
#     db.session.commit()
#     return series


# @series.route('/series/<int:id>', methods=['DELETE'])
# @authenticate(token_auth)
# @other_responses({403: 'Not allowed to delete the series'})
# def delete(id):
#     """Delete a series"""
#     series = db.session.get(Series, id) or abort(404)
#     if series.user != token_auth.current_user():
#         abort(403)
#     db.session.delete(series)
#     db.session.commit()
#     return '', 204


# @series.route('/feed', methods=['GET'])
# @authenticate(token_auth)
# @paginated_response(multi_series_schema, order_by=Series.title,
#                     order_direction='asc',
#                     pagination_schema=DateTimePaginationSchema)
# def feed():
#     """Retrieve the user's series feed"""
#     user = token_auth.current_user()
#     return user.followed_series_select()

# @series.route('series/images/<int:id>',methods=['GET'])
# # @authenticate(token_auth)
# def upload(id):
#     """Retrieve series image"""
#     series = db.session.get(Series, id)
#     print(series.thumbnail)
#     return send_file(current_app.config['cover_path']+f"\\{series.thumbnail}")