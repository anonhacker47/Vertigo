from flask import Blueprint, jsonify, request
from apifairy import authenticate, other_responses

from api.utils.auth import token_auth
from api.insights.collection import load_collection
from api.insights.up_next import build_up_next
from api.insights.queues import build_reading_queue, build_get_next
from api.insights.activity import build_activity
from api.insights.records import build_records
from api.insights.facts import build_facts
from api.insights.on_this_day import build_on_this_day
from api.insights.ranking import ranked

insights = Blueprint('insights', __name__)


def _collection():
    user = token_auth.current_user()
    return user, load_collection(user.id)


@insights.route('/insights/up-next', methods=['GET'])
@authenticate(token_auth)
@other_responses({401: 'Not authenticated'})
def up_next():
    """The issue to read next, why, and two alternates"""
    _, collection = _collection()
    return jsonify(build_up_next(collection))


@insights.route('/insights/reading-queue', methods=['GET'])
@authenticate(token_auth)
@other_responses({401: 'Not authenticated'})
def reading_queue():
    """Series with unread issues on the shelf, hero's series excluded"""
    _, collection = _collection()
    entries = ranked(collection)
    hero_series_id = entries[0][2].series.id if entries else None
    return jsonify(build_reading_queue(collection, exclude_series_id=hero_series_id))


@insights.route('/insights/get-next', methods=['GET'])
@authenticate(token_auth)
@other_responses({401: 'Not authenticated'})
def get_next():
    """Started runs closest to complete"""
    _, collection = _collection()
    return jsonify(build_get_next(collection))


@insights.route('/insights/activity', methods=['GET'])
@authenticate(token_auth)
@other_responses({401: 'Not authenticated'})
def activity():
    """Bought vs read per period plus pace figures (?range=ytd|last_year|all)"""
    _, collection = _collection()
    return jsonify(build_activity(collection, request.args.get('range', 'ytd')))


@insights.route('/insights/records', methods=['GET'])
@authenticate(token_auth)
@other_responses({401: 'Not authenticated'})
def records():
    """Firsts, records and the completed shelf"""
    user, collection = _collection()
    return jsonify(build_records(collection, user))


@insights.route('/insights/facts', methods=['GET'])
@authenticate(token_auth)
@other_responses({401: 'Not authenticated'})
def facts():
    """On this day plus a daily selection of facts"""
    user, collection = _collection()
    return jsonify({
        'on_this_day': build_on_this_day(collection, user),
        'facts': build_facts(collection, user),
    })
