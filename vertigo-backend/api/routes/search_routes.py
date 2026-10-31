"""One box for every shelf: the user's series, issues, publishers, creators and characters."""
import re

from flask import Blueprint, jsonify, request, url_for
from apifairy import authenticate, other_responses
import sqlalchemy as sqla
from sqlalchemy.orm import joinedload

from api import db
from api.models.series import Series
from api.models.issue import Issue
from api.models.series_entities import Publisher, Creator, Character
from api.utils.auth import token_auth

search = Blueprint('search', __name__)

DEFAULT_LIMIT = 5
MAX_LIMIT = 20
ISSUE_QUERY = re.compile(r'^(?P<text>.*?)\s*#?(?P<number>\d+)$')


def _like(column, text):
    return column.ilike(f'%{text}%')


def _image(endpoint, obj):
    return url_for(endpoint, id=obj.id, _external=True) if obj.thumbnail else None


def _series_row(s):
    return {
        'id': s.id, 'title': s.title, 'slug': s.slug, 'series_format': s.series_format,
        'manga': bool(s.manga), 'issue_count': s.issue_count or 0, 'owned_count': s.owned_count or 0,
        'thumbnail': _image('series.get_series_image', s),
    }


def _issue_row(i):
    return {
        'id': i.id, 'number': i.number, 'title': i.title,
        'is_owned': bool(i.is_owned), 'is_read': bool(i.is_read),
        'series': {'id': i.series.id, 'title': i.series.title, 'slug': i.series.slug, 'manga': bool(i.series.manga)},
        'thumbnail': _image('issue.get_issue_image', i) or _image('series.get_series_image', i.series),
    }


def _entity_row(endpoint, e):
    return {'id': e.id, 'title': e.title, 'slug': e.slug, 'thumbnail': _image(endpoint, e)}


def _series(user, text, limit):
    return db.session.scalars(
        user.series_select().where(_like(Series.title, text)).order_by(Series.title).limit(limit)).all()


def _issues(user, text, limit):
    """Custom titles match on the text; a trailing number picks that issue, within a series if one is named."""
    clauses = [sqla.and_(Issue.title != sqla.cast(Issue.number, sqla.String), _like(Issue.title, text))]
    match = ISSUE_QUERY.match(text)
    if match:
        by_number = Issue.number == int(match.group('number'))
        series_part = match.group('text').strip()
        if series_part:
            by_number = sqla.and_(by_number, _like(Series.title, series_part))
        clauses.append(by_number)
    query = (user.issue_select().join(Issue.series).options(joinedload(Issue.series))
             .where(sqla.or_(*clauses)).order_by(Series.title, Issue.number).limit(limit))
    return db.session.scalars(query).all()


def _entities(select, model, endpoint, text, limit):
    rows = db.session.scalars(select.where(_like(model.title, text)).order_by(model.title).limit(limit)).all()
    return [_entity_row(endpoint, e) for e in rows]


@search.route('/search', methods=['GET'])
@authenticate(token_auth)
@other_responses({401: 'Not authenticated'})
def global_search():
    """Search the user's series, issues, publishers, creators and characters by name.

    ``q`` is matched case-insensitively anywhere in the title; ``limit`` caps each group.
    """
    user = token_auth.current_user()
    text = (request.args.get('q') or '').strip()
    try:
        limit = min(max(int(request.args.get('limit', DEFAULT_LIMIT)), 1), MAX_LIMIT)
    except ValueError:
        limit = DEFAULT_LIMIT

    if len(text) < 2 and not text.isdigit():
        return jsonify({'query': text, 'series': [], 'issues': [], 'publishers': [], 'creators': [], 'characters': []})

    return jsonify({
        'query': text,
        'series': [_series_row(s) for s in _series(user, text, limit)],
        'issues': [_issue_row(i) for i in _issues(user, text, limit)],
        'publishers': _entities(user.publisher_select(), Publisher, 'publisher.get_publisher_image', text, limit),
        'creators': _entities(user.creator_select(), Creator, 'creator.get_creator_image', text, limit),
        'characters': _entities(user.character_select(), Character, 'character.get_character_image', text, limit),
    })
