import os
from datetime  import datetime, timezone

from flask import Blueprint, abort, jsonify, request, send_file, send_from_directory
from apifairy import authenticate, body, response, other_responses

from api import db
from api.models.user import User
from api.models.series import Series
from api.models.issue import Issue

from api.schemas.issue_schema import IssueSchema, SlimIssueSchema
from api.utils.auth import token_auth
from api.decorators import paginated_response
from api.schemas.pagination_schema import DateTimePaginationSchema
 

issues = Blueprint('issue', __name__)
issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True)
update_issue_schema = IssueSchema(partial=True)


@issues.route('/series/<int:series_id>/issues', methods=['POST'])
@authenticate(token_auth)
@body(issues_schema)  # Expecting a list of issues
@response(issues_schema, 201)
def new(args, series_id):
    """Create multiple new issues for a series"""

    user = token_auth.current_user()
    series = db.session.get(Series, series_id)

    if not series:
        return jsonify({"error": "Series not found"}), 404

    new_issues = []
    for issue_data in args:
        issue = Issue(
        user=user,
        series=series,
        title=issue_data["title"],
        number=issue_data["number"],
        is_owned=issue_data["is_owned"],
        is_read=issue_data["is_read"],
        bought_date=issue_data.get("bought_date") or (datetime.now(timezone.utc) if issue_data["is_owned"] else None),
        read_date=issue_data.get("read_date") or (datetime.now(timezone.utc) if issue_data["is_read"] else None),
        bought_price=issue_data.get("bought_price")
        )
        db.session.add(issue)
        new_issues.append(issue)

    db.session.commit()

    issues_query = series.issue_select()
    issues_data = db.session.scalars(issues_query).all()
    series.owned_count = sum(i.is_owned for i in issues_data)
    series.read_count = sum(i.is_read for i in issues_data)
    series.issue_count = len(issues_data)
    series.purchase_cost = sum(i.bought_price or 0 for i in issues_data if i.is_owned)
    db.session.commit()

    return new_issues

@issues.route('/series/<int:series_id>/single_issue', methods=['POST'])
@authenticate(token_auth)
@response(issue_schema)
@other_responses({404: 'Series not found'})
def create_single_issue(series_id):
    """Create a new issue for a series"""
    user = token_auth.current_user()
    series = db.session.get(Series, series_id) or abort(404)

    # Get all issues for this series and sort them by number
    issues_query = series.issue_select()
    issues_data = db.session.scalars(issues_query).all()
    sorted_issues = sorted(issues_data, key=lambda issue: issue.number)

    # Determine the last issue
    if not sorted_issues:
        abort(400, "No existing issues in series to base new issue on")

    last_issue = sorted_issues[-1]

    new_issue = Issue(
        title=last_issue.number + 1,
        number=last_issue.number + 1,
        user=user,
        series=series,
        is_read=False,
        is_owned=False,
        bought_price=None,
        bought_date=None,
        read_date=None,
        slug=None,
    )

    db.session.add(new_issue)
    db.session.commit()

    # Recalculate counts
    issues_query = series.issue_select()
    updated_issues = db.session.scalars(issues_query).all()
    series.owned_count = sum(i.is_owned for i in updated_issues)
    series.read_count = sum(i.is_read for i in updated_issues)
    series.issue_count = len(updated_issues)
    series.purchase_cost = sum(i.bought_price or 0 for i in updated_issues if i.is_owned)

    db.session.commit()

    return new_issue


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

   # Check if `owned or read` is True, update `bought_date` and 'read_date'
    if data.get('is_owned') is False:
        issue.bought_date = None
        issue.bought_price = None
    elif data.get('is_owned') is True:
        issue.bought_date = data.get('bought_date') or datetime.now(timezone.utc)

# Read status handling
    if data.get('is_read') is False:
        issue.read_date = None
    elif data.get('is_read') is True:
        issue.read_date = data.get('read_date') or datetime.now(timezone.utc)

    # Recalculate series counters
    issues = issue.series.issue_select()
    issues_data = db.session.scalars(issues).all()
    issue.series.owned_count = sum(i.is_owned for i in issues_data)
    issue.series.read_count = sum(i.is_read for i in issues_data)

    issue.series.purchase_cost = sum(
        i.bought_price or 0 for i in issues_data if i.is_owned
    )

    db.session.commit()
    return issue


@issues.route('/series/issues/<int:id>/', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the series'})
def delete(id):
    """Delete an issue"""
    issue = db.session.get(Issue, id) or abort(404)
    if issue.user != token_auth.current_user():
        abort(403)

    issues = issue.series.issue_select()
    issues_data = db.session.scalars(issues).all()
    sorted_issues = sorted(issues_data, key=lambda issue: issue.number)

    is_last = sorted_issues and sorted_issues[-1].number == issue.number

    if is_last:
        db.session.delete(issue)
            # Recalculate series counters
        issues = issue.series.issue_select()
        issues_data = db.session.scalars(issues).all()
        issue.series.owned_count = sum(i.is_owned for i in issues_data)
        issue.series.read_count = sum(i.is_read for i in issues_data)
        issue.series.issue_count = len(issues_data)
        issue.series.purchase_cost = sum(
            i.bought_price or 0 for i in issues_data if i.is_owned
        )
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Cannot delete issues that are not the last in the series"}), 403




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
