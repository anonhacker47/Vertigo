import os
from datetime  import datetime, timezone

from flask import Blueprint, abort, request, send_file, send_from_directory
from apifairy import authenticate, body, response, other_responses

from api import db
from api.models.user import User
from api.models.series import Series
from api.models.issue import Issue

from api.schemas.issue_schema import IssueSchema
from api.utils.auth import token_auth
from api.decorators import paginated_response
from api.schemas.pagination_schema import DateTimePaginationSchema
 

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
    count = series.issue_count + 1
    is_read = 1 if series.read_count == series.issue_count else 0
    is_owned = 1 if series.owned_count == series.issue_count else 0

    for i in range(1,count):
        title = f"volume {i}"
        issue = Issue(user=user, series=series, title=title,
                      is_read=is_read, is_owned=is_owned)
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
@paginated_response(issues_schema, order_by=Issue.title,
                    order_direction='asc',
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

@issues.route('/series/<int:id>/issue_count', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: 'User not found'})
def issue_count(id):
    """Retrieve issue counts from a series"""
    series = db.session.get(Series, id) or abort(404)
    issues = series.issue_select()
    data = db.session.scalars(issues).all()
    # Calculate the counts
    owned_count = sum(issue.is_owned for issue in data)
    read_count = sum(issue.is_read for issue in data)

    response = {
        "total_count":len(data),
        "owned_count": owned_count,
        "read_count": read_count,
    }

    return response


@issues.route('/series/issues/<int:id>/', methods=['PUT'])
@authenticate(token_auth)
@body(update_issue_schema)
@response(issue_schema)
@other_responses({403: 'Not allowed to edit this issue',
                  404: 'Issue not found'})
def put(data, id):
    """Edit an issue"""
    issue = db.session.get(Issue, id) or abort(404)
    if issue.user != token_auth.current_user():
        abort(403)
    issue.update(data)

    # Recalculate counts for the series
    issues = issue.series.issue_select()
    issues_data = db.session.scalars(issues).all()
    is_owned_count = sum(issue.is_owned for issue in issues_data)
    is_read_count = sum(issue.is_read for issue in issues_data)

    # Update the series counts
    issue.series.owned_count = is_owned_count
    issue.series.read_count = is_read_count

    # Check if `owned or read` is True, update `bought_date` and 'read_date'
    if data.get('is_owned') == False:
        issue.bought_date = None
    if data.get('is_read') == False:
        issue.read_date = None
    if data.get('is_owned'):
        issue.bought_date = datetime.now(timezone.utc)
    if data.get('is_read'):
        issue.read_date = datetime.now(timezone.utc)

    db.session.commit()
    return issue


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
