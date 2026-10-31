from flask import Blueprint, jsonify
from apifairy import authenticate, other_responses

from api.jobs import registry
from api.utils.auth import token_auth

jobs = Blueprint('jobs', __name__)


@jobs.route('/jobs', methods=['GET'])
@authenticate(token_auth)
@other_responses({401: 'Not authenticated'})
def list_jobs():
    """The current user's background jobs that are queued or running."""
    user = token_auth.current_user()
    return jsonify({'jobs': [job.to_dict() for job in registry.for_user(user.id)]})
