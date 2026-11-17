from flask import jsonify

from flask import Blueprint, abort, request, send_file
from apifairy import authenticate, response, other_responses
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload
from api import db
from api.models.series import Series
import api.models.series_entities as series_entities
from api.models.issue import Issue

from api.schemas.series_schema import SeriesSchema

from api import media

from api.utils.auth import token_auth
from api.utils.ownership import owned_or_403
from api.decorators import paginated_response
from api.routes.series_sorts import SERIES_SORTS
from api.routes.series_filters import apply_status_filters
from api.schemas.pagination_schema import DateTimePaginationSchema
from api.utils.entity_manager import create_or_get_entity, safe_json_list, ENTITY_MODEL_MAP
from api.helpers.cover_bg_generator import background_path, submit_background_regeneration

series = Blueprint('series', __name__)
series_schema = SeriesSchema()
multi_series_schema = SeriesSchema(many=True)
list_series_schema = SeriesSchema(many=True, exclude=('character', 'creator', 'description', 'notes', 'user'))
LIST_LOADS = (selectinload(Series.publisher), selectinload(Series.genre))
update_series_schema = SeriesSchema(partial=True)

@series.route('/series', methods=['POST'])
@authenticate(token_auth)
def new():
    """Create a new series"""
    user = token_auth.current_user()

    # Parse FormData fields
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    notes = request.form.get('notes', '')
    series_format = request.form.get('series_format', '')
    issue_count = int(request.form.get('issue_count', 0))
    read_count = int(request.form.get('read_count', 0))
    owned_count = int(request.form.get('owned_count', 0))
    thumbnail = request.form.get('thumbnail', '').strip()
    metron_id = request.form.get('metron_id', None)
    metron_url = request.form.get('metron_url', None)
    manga = request.form.get('manga', 'false').lower() == 'true'

    series = Series(
        user=user,
        title=title,
        description=description,
        notes=notes,
        series_format=series_format,
        issue_count=issue_count,
        read_count=read_count,
        owned_count=owned_count,
        metron_id=metron_id,
        metron_url=metron_url,
        manga=manga,
    )
    db.session.add(series)

    entities = {
        "genre": safe_json_list(request.form.get("genre")),
        "creator": safe_json_list(request.form.get("creator")),
        "character": safe_json_list(request.form.get("character")),
        "publisher": safe_json_list(request.form.get("publisher")),
    }

    for entity_type, items in entities.items():
        model = ENTITY_MODEL_MAP[entity_type]
        rel = getattr(series, entity_type)
        
        for item in items:

            name = item["value"] if isinstance(item, dict) else item
            external_id = None
            if isinstance(item, dict):
                external_id = item.get("mal_id") if manga else item.get("metron_id")
                
            entity = create_or_get_entity(
                model, name, user, entity_type, external_id, series_is_manga=manga
            )

            if not entity:
                continue

            if entity not in rel:
                rel.append(entity)

    db.session.flush()  # the cover is stored under series/<id>/
    try:
        state, relpath, color = media.apply_thumbnail_field(
            user.id, request.form, request.files, 'thumbnail',
            rel_dir=media.series_dir(series.id), filename='cover',
            current=None, want_color=True,
        )
    except media.MediaError as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save thumbnail: {e}"}), 400
    if state == 'set':
        series.thumbnail = relpath
        series.touch_thumbnail()
        series.dominant_color = color
        submit_background_regeneration(user.id)

    db.session.commit()
    return series_schema.dump(series), 201


@series.route('/series/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(series_schema)
@other_responses({403: 'Not allowed to view this series', 404: 'Series not found'})
def get(id):
    """Retrieve a series by id"""
    return owned_or_403(Series, id)


@series.route('/users/series', methods=['GET'])
@authenticate(token_auth)
@paginated_response(list_series_schema, order_by=Series.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema,
                    sorts=SERIES_SORTS, tiebreak=Series.title)
@other_responses({404: 'User not found'})
def user_all():
    """Retrieve all series of a user with optional search and filters"""
    user = token_auth.current_user()
    qs = user.series_select() 
    

    base_total = db.session.scalar(
        select(func.count()).select_from(qs)
    )

    # Optional search & filters from query parameters
    search_query = request.args.get("query", "").strip()
    genre = request.args.get("genre")
    character = request.args.get("character")
    creator = request.args.get("creator")
    publisher = request.args.get("publisher")
    series_format = request.args.get("series_format")

    # Apply filters conditionally
    if search_query:
        qs = qs.filter(
            or_(
                Series.title.ilike(f"%{search_query}%"),
                Series.description.ilike(f"%{search_query}%")
            )
        )
    if genre:
        qs = qs.filter(Series.genre.any(title=genre))
    if creator:
        qs = qs.filter(Series.creator.any(title=creator))    
    if publisher:
        qs = qs.filter(Series.publisher.any(title=publisher))
    if character:
        qs = qs.filter(Series.character.any(title=character))
    if series_format:
        qs = qs.filter(Series.series_format == series_format)
    qs = apply_status_filters(qs, request.args)

    return qs.options(*LIST_LOADS), {"base_total": base_total}


@series.route('/series/<int:id>', methods=['PUT'])
@authenticate(token_auth)
def update_series(id):
    """Edit a series"""
    user = token_auth.current_user()
    series = db.session.get(Series, id) or abort(404)

    if series.user != user:
        abort(403)

    form = request.form

    if 'title' in form:
        series.title = form.get('title', '').strip()

    if 'description' in form:
        series.description = form.get('description', '').strip()

    if 'notes' in form:
        series.notes = form.get('notes', '').strip()

    if 'series_format' in form:
        series.series_format = form.get('series_format', '').strip()

    if 'issue_count' in form:
        series.issue_count = int(form.get('issue_count', 0))

    if 'read_count' in form:
        series.read_count = int(form.get('read_count', 0))

    if 'owned_count' in form:
        series.owned_count = int(form.get('owned_count', 0))

    if 'user_rating' in form:
        rating = form.get('user_rating')
        if rating in (None, '', 'null'):
            series.user_rating = None
        else:
            series.user_rating = float(rating)

    # Metron link: an empty value clears it.
    if 'metron_id' in form:
        metron_id = (form.get('metron_id') or '').strip()
        series.metron_id = metron_id if metron_id not in ('', 'null') else None

    if 'metron_url' in form:
        metron_url = (form.get('metron_url') or '').strip()
        series.metron_url = metron_url if metron_url not in ('', 'null') else None

    entities = {
        entity_type: safe_json_list(form.get(entity_type))
        for entity_type in ("genre", "creator", "character", "publisher")
        if entity_type in form
    }

    for entity_type, items in entities.items():
        model = ENTITY_MODEL_MAP[entity_type]
        new_entities = []

        for item in items:
            name = item["value"] if isinstance(item, dict) else item
            if not name:
                continue
            external_id = None
            if isinstance(item, dict):
                external_id = item.get("mal_id") if series.manga else item.get("metron_id")

            entity = create_or_get_entity(
                model, name, user, entity_type, external_id, series_is_manga=series.manga
            )
            if entity:
                new_entities.append(entity)

        setattr(series, entity_type, new_entities)
        
    try:
        state, relpath, color = media.apply_thumbnail_field(
            user.id, form, request.files, 'thumbnail',
            rel_dir=media.series_dir(series.id), filename='cover',
            current=series.thumbnail, want_color=True,
        )
    except media.MediaError as e:
        return jsonify({"error": f"Failed to update thumbnail: {e}"}), 400

    if state == 'set':
        series.thumbnail = relpath
        series.touch_thumbnail()
        series.dominant_color = color
        submit_background_regeneration(user.id)
    elif state == 'cleared':
        series.thumbnail = None
        series.dominant_color = None
        submit_background_regeneration(user.id)
  
    db.session.commit()
    return series_schema.dump(series)


@series.route('/series/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the series'})
def delete(id):
    """Delete a series"""
    series = db.session.get(Series, id) or abort(404)
    if series.user != token_auth.current_user():
        abort(403)

    issues = db.session.query(Issue).filter(Issue.series_id==id).all()

    for issue in issues:
        db.session.delete(issue)    
    db.session.delete(series)

    user_id = series.user_id
    media.remove_dir(user_id, media.series_dir(series.id))   # cover plus issue covers
    submit_background_regeneration(user_id)

    db.session.commit()
    return '', 204


@series.route('/feed', methods=['GET'])
@authenticate(token_auth)
@paginated_response(list_series_schema, order_by=Series.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def feed():
    """Retrieve the user's series feed"""
    user = token_auth.current_user()
    return user.followed_series_select().options(*LIST_LOADS)


@series.route('series/image/<int:id>',methods=['GET'])
def get_series_image(id):
    """Retrieve the series thumbnail"""
    series = db.session.get(Series, id)
    if series is None:
        return jsonify("Series not found"), 404
    return media.send(series.user_id, series.thumbnail)

@series.route('/series/filters', methods=['GET'])
@authenticate(token_auth)
def filter_values():
    """Distinct publishers, creators, characters, genres and formats across the user's series, as {id, value} lists"""
    user = token_auth.current_user()

    def options(values):
        return [{'id': str(i + 1), 'value': v} for i, v in enumerate(sorted({v for v in values if v}))]

    def titles(model):
        return db.session.scalars(select(model.title).where(model.user_id == user.id).distinct()).all()

    formats = db.session.scalars(select(Series.series_format).where(Series.user_id == user.id).distinct()).all()
    return jsonify({
        'publisher': options(titles(series_entities.Publisher)),
        'creator': options(titles(series_entities.Creator)),
        'character': options(titles(series_entities.Character)),
        'genre': options(titles(series_entities.Genre)),
        'series_format': options(formats),
    })

@series.route('/series/thumbnail/bg', methods=['GET'])
def get_series_with_thumbnail():
    """Retrieve The Login Page Background"""
    cover_bg = background_path()

    try:
        return send_file(cover_bg)
    except FileNotFoundError:
        return jsonify("Image file not found"), 404
    except Exception as e:
        return jsonify(f"Error retrieving image: {str(e)}"), 500

@series.route('/series/<int:id>/neighbors', methods=['GET'])
@authenticate(token_auth)
def neighbors(id):
    """Retrieve the previous and next series based on alphabetical order."""

    user = token_auth.current_user()

    series_obj = owned_or_403(Series, id)
    current_title = series_obj.title

    prev_series = (
        db.session.query(Series)
        .filter(Series.user_id == user.id, Series.title < current_title)
        .order_by(Series.title.desc())
        .first()
    )

    next_series = (
        db.session.query(Series)
        .filter(Series.user_id == user.id, Series.title > current_title)
        .order_by(Series.title.asc())
        .first()
    )

    def format_item(item):
        if item is None:
            return None
        return {
            "id": item.id,
            "slug": item.slug,
            "title": item.title,
        }

    return jsonify({
        "previous": format_item(prev_series),
        "next": format_item(next_series),
    })
