import os
from pstats import SortKey
import random
from flask import current_app, json, jsonify
import sqlite3

from flask import Blueprint, abort, request, send_file, send_from_directory
from apifairy import authenticate, body, response, other_responses
from sqlalchemy import or_
from api import db
from api.models.user import User
from api.models.series import Series
import api.models.series_entities as series_entities
from api.models.issue import Issue

from api.schemas.series_schema import SeriesSchema
from api.schemas.empty_schema import EmptySchema

from api.utils.auth import token_auth
from api.utils.series_field import create_or_get_entities
from api.decorators import paginated_response
from api.schemas.pagination_schema import DateTimePaginationSchema
from api.helpers.thumbnail_processing import download_series_thumbnail, save_series_thumbnail,delete_series_thumbnail


series = Blueprint('series', __name__)
series_schema = SeriesSchema()
multi_series_schema = SeriesSchema(many=True)
update_series_schema = SeriesSchema(partial=True)


@series.route('/series', methods=['POST'])
@authenticate(token_auth)
def new():
    """Create a new series"""
    user = token_auth.current_user()

    # Parse FormData fields
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    series_format = request.form.get('series_format', '')
    issue_count = int(request.form.get('issue_count', 0))
    read_count = int(request.form.get('read_count', 0))
    owned_count = int(request.form.get('owned_count', 0))
    main_character = request.form.get('main_character', None)
    thumbnail = request.form.get('thumbnail', '').strip()

    # Parse JSON fields within FormData
    genre = request.form.get('genre', '[]')
    creator = request.form.get('creator', '[]')
    publisher = request.form.get('publisher', '[]')

    entities = {
        'genre': json.loads(genre),
        'creator': json.loads(creator),
        'publisher': [publisher],
        'main_character': [main_character] if main_character else []
    }

    # Create series instance
    series = Series(
        user=user,
        title=title,
        description=description,
        series_format=series_format,
        issue_count=issue_count,
        read_count=read_count,
        owned_count=owned_count,
    )
    db.session.add(series)

    # Handle entities
    for entity_type, titles in entities.items():
        entity_items = create_or_get_entities(entity_type, titles)
        for item in entity_items:
            getattr(series, entity_type).append(item)


    # Handle thumbnail file if it is link
    if thumbnail.startswith('http'):
        # URL case
        thumbnail_filename, dominant_color = download_series_thumbnail(thumbnail, title,'cover_path')
        if thumbnail_filename:
            series.thumbnail = thumbnail_filename
            series.dominant_color = dominant_color
    # Handle thumbnail file if it exists
    elif 'thumbnail' in request.files:
        file = request.files['thumbnail']
        thumbnail_filename, dominant_color = save_series_thumbnail(file, title,'cover_path')
        series.thumbnail = thumbnail_filename
        series.dominant_color = dominant_color

    db.session.commit()
    return series_schema.dump(series), 201

@series.route('/series/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(series_schema)
@other_responses({404: 'Series not found'})
def get(id):
    """Retrieve a series by id"""
    return db.session.get(Series, id) or abort(404)

@series.route('/series', methods=['GET'])
@authenticate(token_auth)
@paginated_response(multi_series_schema, order_by=Series.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all series"""
    return Series.select()


@series.route('/users/<int:id>/series', methods=['GET'])
@authenticate(token_auth)
@paginated_response(multi_series_schema, order_by=Series.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
@other_responses({404: 'User not found'})
def user_all(id):
    """Retrieve all series of a user with optional search and filters"""
    user = db.session.get(User, id) or abort(404)
    qs = user.series_select() 
    
    # Optional search & filters from query parameters
    search_query = request.args.get("query", "").strip()
    genre = request.args.get("genre")
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
    if series_format:
        qs = qs.filter(Series.series_format == series_format)

    return qs


@series.route('/series/<int:id>', methods=['PUT'])
@authenticate(token_auth)
def update_series(id):
    """Edit a series"""
    user = token_auth.current_user()
    series = db.session.get(Series, id) or abort(404)

    if series.user != user:
        abort(403)

    form = request.form

    # Update fields only if present
    if 'title' in form:
        series.title = form.get('title', '').strip()

    if 'description' in form:
        series.description = form.get('description', '').strip()

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

    # Handle JSON fields if present
    entities = {}
    if 'genre' in form:
        entities['genre'] = json.loads(form.get('genre', '[]'))

    if 'creator' in form:
        entities['creator'] = json.loads(form.get('creator', '[]'))

    if 'publisher' in form:
        entities['publisher'] = [form.get('publisher')] if form.get('publisher') else []

    if 'main_character' in form and form.get('main_character'):
        entities['main_character'] = [form.get('main_character')]

    for entity_type, titles in entities.items():
        entity_items = create_or_get_entities(entity_type, titles)
        setattr(series, entity_type, entity_items)

    # Handle thumbnail
    thumbnail = form.get('thumbnail', '').strip() if 'thumbnail' in form else ''
    if thumbnail.startswith('http'):
        thumbnail_filename, dominant_color = download_series_thumbnail(thumbnail, form.get('title', ''),'cover_path')
        if thumbnail_filename:
            series.thumbnail = thumbnail_filename
            series.dominant_color = dominant_color
    elif 'thumbnail' in request.files:
        file = request.files['thumbnail']
        thumbnail_filename, dominant_color = save_series_thumbnail(file, form.get('title', ''),'cover_path')
        series.thumbnail = thumbnail_filename
        series.dominant_color = dominant_color

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
    thumbnail =  series.thumbnail 

    issues = db.session.query(Issue).filter(Issue.series_id==id).all()
    for issue in issues:
        db.session.delete(issue)    
    db.session.delete(series)
    
    if os.path.exists(current_app.config['cover_path']+f"\\{thumbnail}"):
        os.remove(current_app.config['cover_path']+f"\\{thumbnail}")
    else:
        print("The file does not exist") 

    db.session.commit()
    return '', 204


@series.route('/feed', methods=['GET'])
@authenticate(token_auth)
@paginated_response(multi_series_schema, order_by=Series.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def feed():
    """Retrieve the user's series feed"""
    user = token_auth.current_user()
    return user.followed_series_select()

@series.route('series/image/<int:id>',methods=['GET'])
def get_series_image(id):
    """Retrieve the series thumbnail"""
    series = db.session.get(Series, id)

    if series is None:
        return jsonify("Series not found"), 404

    if series.thumbnail is None:
        return jsonify("noimage")

    try:
        # print(current_app.config['cover_path']+ f"\\{series.thumbnail}")
        return send_file(os.path.join(current_app.config['cover_path'], series.thumbnail))
    except FileNotFoundError:
        return jsonify("Image file not found"), 404
    except Exception as e:
        # Handle other potential exceptions (e.g., permission errors)
        return jsonify(f"Error retrieving image: {str(e)}"), 500
    
@series.route('/series/key', methods=['GET'])
@authenticate(token_auth)
def key():
    """Retrieve series key"""
    obj = db.session.query(Series).order_by(Series.id.desc()).first()
    if obj is None:
        return jsonify("0")
    else:
        return jsonify(f"{obj.id}")
    
@series.route('/series/filter/<table>', methods=['GET'])
@authenticate(token_auth)
def get_series_by_table(table):
    """Retrieve values from a specific table across all series objects."""

    table_class = {
        'main_character': series_entities.MainCharacter,
        'genre': series_entities.Genre,
        'creator': series_entities.Creator,
        'publisher': series_entities.Publisher,
        'series_format': Series.series_format
    }.get(table.lower())
    if table_class is None:
        return jsonify({'error': 'Invalid table name'}), 400
        
    if table == 'series_format':
        values = db.session.query(Series.series_format).distinct().filter(Series.series_format.isnot(None)).all()
        values = {value[0] for value in values if value[0]}
        return jsonify(sorted(list(values)))
    
    values = db.session.query(table_class.title).distinct().all()
    values = {value.title for value in values}

    # Sort and format the final list
    values = sorted(values)
    values = [{'id': str(i + 1), 'value': value} for i, value in enumerate(values)]
    return jsonify(values)

@series.route('/series/thumbnail/bg', methods=['GET'])
def get_series_with_thumbnail():
    """Retrieve IDs of series with non-null thumbnails"""
    series_with_thumbnail = db.session.query(Series.id).filter(Series.thumbnail.isnot(None)).all()
    series_ids = [series[0] for series in series_with_thumbnail]
    
    if series_ids:
        while len(series_ids) < 80:
            series_ids.extend(series_ids)
        random.shuffle(series_ids)
        series_ids = series_ids[:80]
    else:
        series_ids = []
    
    return jsonify(series_ids)

@series.route('/series/<int:id>/neighbors', methods=['GET'])
@authenticate(token_auth)
def neighbors(id):
    """Retrieve the previous and next series based on alphabetical order."""

    user = token_auth.current_user()

    series_obj = db.session.get(Series, id) or abort(404)
    current_title = series_obj.title

    prev_series = (
        db.session.query(Series)
        .filter(Series.user_id == user.id, Series.title < current_title)
        .order_by(Series.title.desc())
        .first()
    )

    # Next series for the same user
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
            "slug": item.slug,   # adjust field name
        }

    return jsonify({
        "previous": format_item(prev_series),
        "next": format_item(next_series),
    })