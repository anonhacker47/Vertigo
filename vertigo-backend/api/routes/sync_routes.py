from flask import Blueprint, request, jsonify
from apifairy import authenticate
from datetime import datetime, timezone
import sqlalchemy as sqla

from api import db
from api.models.series import Series
from api.models.issue import Issue
from api.models.deleted_record import DeletedRecord
from api.schemas.series_schema import SeriesSchema
from api.schemas.issue_schema import IssueSchema
from api.utils.auth import token_auth

sync = Blueprint('sync', __name__)
series_schema = SeriesSchema(many=True)
issues_schema = IssueSchema(many=True)

@sync.route('/sync', methods=['GET'])
@authenticate(token_auth)
def get_sync():
    """Sync data since a specific timestamp"""
    user = token_auth.current_user()
    since_str = request.args.get('since')
    
    since = None
    if since_str:
        try:
            since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO 8601."}), 400

    # Query active series
    series_query = sqla.select(Series).where(Series.user_id == user.id)
    if since:
        series_query = series_query.where(Series.last_updated > since)
    
    active_series = db.session.scalars(series_query).all()

    # Query active issues
    issues_query = sqla.select(Issue).where(Issue.user_id == user.id)
    if since:
        issues_query = issues_query.where(Issue.last_updated > since)
    
    active_issues = db.session.scalars(issues_query).all()

    # Query deleted records
    deleted_query = sqla.select(DeletedRecord).where(DeletedRecord.user_id == user.id)
    if since:
        deleted_query = deleted_query.where(DeletedRecord.deleted_at > since)
    
    deleted_records = db.session.scalars(deleted_query).all()
    
    deleted_series_ids = [d.object_id for d in deleted_records if d.table_name == 'series']
    deleted_issues_ids = [d.object_id for d in deleted_records if d.table_name == 'issue']

    return jsonify({
        "series": series_schema.dump(active_series),
        "issues": issues_schema.dump(active_issues),
        "deleted": {
            "series": deleted_series_ids,
            "issues": deleted_issues_ids
        }
    })
