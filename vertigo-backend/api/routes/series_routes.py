import os
import random
from flask import current_app, json, jsonify

from flask import Blueprint, abort, request, send_file
from apifairy import authenticate, response, other_responses
from sqlalchemy import func, or_, select
from api import db
from api.models.series import Series
import api.models.series_entities as series_entities
from api.models.issue import Issue

from api.schemas.series_schema import SeriesSchema

from api.utils.files import get_user_path

from api.utils.auth import token_auth
from api.decorators import paginated_response
from api.schemas.pagination_schema import DateTimePaginationSchema
from api.helpers.thumbnail_processing import download_thumbnail, handle_series_thumbnail, save_thumbnail,delete_thumbnail
from api.utils.entity_manager import create_or_get_entity, safe_json_list, ENTITY_MODEL_MAP
from api.helpers.cover_bg_generator import BACKGROUND_FILE

series = Blueprint('series', __name__)
series_schema = SeriesSchema()
multi_series_schema = SeriesSchema(many=True)
update_series_schema = SeriesSchema(partial=True)
series_thumbnail_folder = "Covers"

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
    thumbnail = request.form.get('thumbnail', '').strip()
    metron_id = request.form.get('metron_id', None)
    metron_url = request.form.get('metron_url', None)

    series = Series(
        user=user,
        title=title,
        description=description,
        series_format=series_format,
        issue_count=issue_count,
        read_count=read_count,
        owned_count=owned_count,
        metron_id=metron_id,
        metron_url=metron_url,
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
            metron_id = item.get("metron_id") if isinstance(item, dict) else None
            entity = create_or_get_entity(
                model, name, user, entity_type, metron_id
            )

            if not entity:
                continue

            if not rel.filter(model.id == entity.id).first():
                rel.append(entity)

    handle_series_thumbnail(
        series=series,
        thumbnail=thumbnail,
        files=request.files,
        title=title,
        user_id=user.id,
        folder=series_thumbnail_folder,
    )

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


@series.route('/users/series', methods=['GET'])
@authenticate(token_auth)
@paginated_response(multi_series_schema, order_by=Series.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
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

    return qs, {"base_total": base_total}


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
            metron_id = item.get("metron_id") if isinstance(item, dict) else None
            entity = create_or_get_entity(
                model, name, user, entity_type, metron_id
            )

            if not entity:
                continue

            if not rel.filter(model.id == entity.id).first():
                rel.append(entity)

    thumbnail = form.get('thumbnail', '').strip() if 'thumbnail' in form else ''
    if thumbnail and thumbnail != "noimage" or 'thumbnail' in request.files:

        old_filename = series.thumbnail  
        new_filename = None
        new_color = None
        error_occurred = False

        if thumbnail == old_filename or thumbnail != "noimage":
            error_occurred = False

        else:
            try:
                if thumbnail.startswith('http'):
                    new_filename, new_color = download_thumbnail(
                        thumbnail,
                        series.title,
                        user.id,
                        series_thumbnail_folder
                    )
    
                elif 'thumbnail' in request.files:
                    file = request.files['thumbnail']
                    new_filename, new_color = save_thumbnail(
                        file,
                        series.title,
                        user.id,
                        series_thumbnail_folder
                    )
    
                if not new_filename:
                    error_occurred = True
    
            except Exception as e:
                error_occurred = True
                print("Thumbnail update failed:", e)
    
            if error_occurred:
                return jsonify({"error": "Failed to update thumbnail"}), 400
    
            if old_filename:
                delete_thumbnail(old_filename, user.id, series_thumbnail_folder)
    
            series.thumbnail = new_filename
            series.dominant_color = new_color
  
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

    if series.thumbnail:    
        cover_dir = get_user_path(series.user.id, series_thumbnail_folder)
        file_path = os.path.join(cover_dir, series.thumbnail)
    
        delete_thumbnail(file_path, series.user.id, series_thumbnail_folder)

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

    user = series.user
    user_id = user.id


    if series is None:
        return jsonify("Series not found"), 404

    if series.thumbnail is None:
        return jsonify("noimage")
    
    base = get_user_path(user_id, series_thumbnail_folder)
    file_path = os.path.join(base, series.thumbnail)

    try:
        return send_file(file_path)
    except FileNotFoundError:
        return jsonify("Image file not found"), 404
    except Exception as e:
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

    user = token_auth.current_user()

    table_class = {
        'character': series_entities.Character,
        'genre': series_entities.Genre,
        'creator': series_entities.Creator,
        'publisher': series_entities.Publisher,
        'series_format': Series.series_format
    }.get(table.lower())

    if table_class is None:
        return jsonify({'error': 'Invalid table name'}), 400
        
    if table == 'series_format':
        values = db.session.query(Series.series_format).distinct().filter(Series.user_id == user.id,Series.series_format.isnot(None)).all()
        values = {value[0] for value in values if value[0]}
        return jsonify(sorted(values))    
    
    values = db.session.query(table_class.title).distinct().filter(table_class.user_id == user.id).all()
    values = {value.title for value in values}

    # Sort and format the final list
    values = sorted(values)
    values = [{'id': str(i + 1), 'value': value} for i, value in enumerate(values)]
    return jsonify(values)

@series.route('/series/thumbnail/bg', methods=['GET'])
def get_series_with_thumbnail():
    """Retrieve The Login Page Background"""
    cover_bg = os.path.join(current_app.config['sql_path'],BACKGROUND_FILE)

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

    series_obj = db.session.get(Series, id) or abort(404)
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
        }

    return jsonify({
        "previous": format_item(prev_series),
        "next": format_item(next_series),
    })