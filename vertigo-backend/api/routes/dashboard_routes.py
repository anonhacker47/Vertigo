from flask import jsonify, request, url_for
from sqlalchemy import desc,func
from datetime import datetime, timedelta, timezone


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


@dashboard.route('/users/series/stats', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def user_series_stats():
    """Retrieve series count stats from a user"""

    user = token_auth.current_user()
    user_id = user.id if user else None

    series_count = db.session.query(Series).filter_by(user_id=user_id).count()
    completed_series_count = (
        db.session.query(Series)
        .filter_by(user_id=user_id)
        .filter(Series.owned_count == Series.issue_count)
        .count()
    )
    
    read_series_count = (
        db.session.query(Series)
        .filter_by(user_id=user_id)
        .filter(Series.read_count == Series.issue_count)
        .count()
    )    
    return jsonify({'totalSeriesCount': series_count, 'collectedSeriesCount': completed_series_count,'readSeriesCount': read_series_count})



@dashboard.route('/users/issues/stats', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def user_issues_stats():
    """Retrieve issues count stats from a user"""
    
    user = token_auth.current_user()
    user_id = user.id if user else None

    issue_count = db.session.query(Issue).filter_by(user_id=user_id).count()
    completed_issue_count = (
        db.session.query(Issue)
        .filter_by(user_id=user_id)
        .filter(Issue.is_owned == 1)
        .count()
    )
    read_issue_count = (
        db.session.query(Issue)
        .filter_by(user_id=user_id)
        .filter(Issue.is_read == 1)
        .count()
    )
    return jsonify({'totalIssueCount': issue_count, 'collectedIssueCount': completed_issue_count,'readIssueCount': read_issue_count})


@dashboard.route('/users/<string:field>/<string:type>/count', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def user_field_count(field, type):

    user = token_auth.current_user()
    user_id = user.id if user else None

    """Retrieve count of series by field for a user"""
    count = request.args.get('count', default=10, type=int)

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
        'creator': {
            'model': series_entities.Creator,
            'table': associations.series_creator,
            'column': 'creator_id'
        },
        'character': {
            'model': series_entities.Character,
            'table': associations.series_character,
            'column': 'character_id'
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
            .limit(count)
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
            .limit(count)
            .all()
        )

    field_count_json = [{'value': item[1], 'name': item[0]} for item in field_count]
    return jsonify(field_count_json)

@dashboard.route('/users/recent_purchases', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def get_recent_purchases():
    """Get recent purchases for user"""
    user = token_auth.current_user()
    user_id = user.id if user else None

    recent_purchases = (
        db.session.query(
            Issue.title,
            Issue.number,
            Issue.bought_date,
            Series.id.label('series_id'),
            Series.slug.label('slug'),
            Series.title.label('series_title')
        )
        .join(Series, Series.id == Issue.series_id)
        .filter(Issue.bought_date.isnot(None))
        .filter(Series.user_id == user_id)
        .order_by(desc(Issue.bought_date))
        .limit(5)
        .all()
    )
    
    result = []
    for issue in recent_purchases:
        result.append({
            'title': issue.title,
            'bought_date': issue.bought_date.strftime('%d %b %Y') if issue.bought_date else None,
            'series': issue.series_title,
            'series_id': issue.series_id,
            'slug': issue.slug,
            'image': url_for('series.get_series_image', id=issue.series_id, _external=True) 
        })
    
    return jsonify(result)

@dashboard.route('/users/purchases_per_month', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def get_purchases_per_month():
    user = token_auth.current_user()
    user_id = user.id if user else None

    # Get the year from query params or default to current year
    year = request.args.get('year', default=datetime.now().year, type=int)

    # Calculate start and end of that year
    start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)

    purchases_per_month = db.session.query(
        func.strftime('%Y-%m', Issue.bought_date).label('month'),
        func.count(Issue.id).label('count')
    ).join(Series, Series.id == Issue.series_id) \
     .filter(Issue.bought_date >= start_date, Issue.bought_date < end_date) \
     .filter(Series.user_id == user_id) \
     .group_by('month') \
     .order_by('month') \
     .all()

    result = [{'month': month, 'count': count} for month, count in purchases_per_month]
    return jsonify(result)


@dashboard.route('/users/total_spent', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: {'description': 'User not found'}})
def get_total_spent():
    """Get total amount spent on issues for a user"""

    user = token_auth.current_user()
    user_id = user.id if user else None

    total_spent = (
        db.session.query(func.coalesce(func.sum(Issue.bought_price), 0))
        .join(Series, Series.id == Issue.series_id)
        .filter(Issue.is_owned == 1)
        .filter(Series.user_id == user_id)
        .scalar()
    )

    return jsonify({'totalSpent': round(total_spent, 2)})