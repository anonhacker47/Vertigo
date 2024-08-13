import os
from pstats import SortKey
import random
from flask import current_app, json, jsonify
import sqlite3

from flask import Blueprint, abort, request, send_file, send_from_directory
from apifairy import authenticate, body, response, other_responses

from api import db
from api.models.user import User
from api.models.series import Series
import api.models.series_entities as series_entities
from api.models.issue import Issue

from api.schemas.series_schema import SeriesSchema
from api.schemas.empty_schema import EmptySchema

from api.utils.auth import token_auth
from api.utils.series_field import create_or_get_entities, create_or_get_main_character
from api.decorators import paginated_response
from api.schemas.pagination_schema import DateTimePaginationSchema
from api.helpers.thumbnail_processing import save_series_thumbnail,delete_series_thumbnail


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
    main_char = request.form.get('main_char', None)
    main_char_type = request.form.get('main_char_type', None)

    # Parse JSON fields within FormData
    genre = request.form.get('genre', '[]')
    writer = request.form.get('writer', '[]')
    artist = request.form.get('artist', '[]')
    editor = request.form.get('editor', '[]')
    publisher = request.form.get('publisher', '[]')

    entities = {
        'genre': json.loads(genre),
        'editor': json.loads(editor),
        'writer': json.loads(writer),
        'artist': json.loads(artist),
        'publisher': [publisher],
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
        main_char_id=None,  # This will be updated if main_char is provided
        main_char_type=main_char_type,
    )
    db.session.add(series)

    # Handle entities
    for entity_type, titles in entities.items():
        entity_items = create_or_get_entities(entity_type, titles)
        for item in entity_items:
            getattr(series, entity_type).append(item)

    if main_char:
        main_char_instance = create_or_get_main_character(main_char_type, main_char)
        series.main_char_id = main_char_instance.id

    # Handle thumbnail file if it exists
    if 'thumbnail' in request.files:
        file = request.files['thumbnail']
        thumbnail_filename, dominant_color = save_series_thumbnail(file, title)
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
    """Retrieve all series from a user"""
    user = db.session.get(User, id) or abort(404)
    return user.series_select()


@series.route('/series/<int:id>', methods=['PUT'])
@authenticate(token_auth)
def update_series(id):
    """Edit a series"""
    user = token_auth.current_user()
    series = db.session.get(Series, id) or abort(404)

    if series.user != user:
        abort(403)

    # Parse FormData fields
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    series_format = request.form.get('series_format', '')
    issue_count = int(request.form.get('issue_count', 0))
    read_count = int(request.form.get('read_count', 0))
    owned_count = int(request.form.get('owned_count', 0))
    main_char = request.form.get('main_char', None)
    main_char_type = request.form.get('main_char_type', None)

    # Parse JSON fields within FormData
    genre = request.form.get('genre', '[]')
    writer = request.form.get('writer', '[]')
    artist = request.form.get('artist', '[]')
    editor = request.form.get('editor', '[]')
    publisher = request.form.get('publisher', '[]')

    entities = {
        'genre': json.loads(genre),
        'editor': json.loads(editor),
        'writer': json.loads(writer),
        'artist': json.loads(artist),
        'publisher': [publisher],
    }

    # Handle thumbnail file if it exists
    thumbnail_filename = None
    if 'thumbnail' in request.files:
        file = request.files['thumbnail']
        thumbnail_filename, dominant_color = save_series_thumbnail(file, title)
        if series.thumbnail:
            delete_series_thumbnail(series.thumbnail)
        series.thumbnail = thumbnail_filename
        series.dominant_color = dominant_color

    # Update series instance
    series.title = title
    series.description = description
    series.series_format = series_format
    series.issue_count = issue_count
    series.read_count = read_count
    series.owned_count = owned_count
    series.main_char_type = main_char_type

    # Handle entities
    for entity_type, titles in entities.items():
        entity_items = create_or_get_entities(entity_type, titles)
        setattr(series, entity_type, entity_items)

    # Handle main character
    if main_char:
        main_char_instance = create_or_get_main_character(main_char_type, main_char)
        series.main_char_id = main_char_instance.id
        series.main_char_type = main_char_type
    else:
        series.main_char_id = None
        series.main_char_type = None

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
        return send_file(current_app.config['cover_path'] + f"\\{series.thumbnail}")
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
    
    # # Get all series objects
    # if table_class is None:
    #     if table == "publisher" or "main_char":
    #         values = db.session.query(getattr(Series, table)).distinct().all()
    #         # Extract the desired field values
    #         values = [value[0] for value in values if value[0]]
    #         # Remove duplicates (optional)
    #         values = list(set(values))
    #         values.sort() 
    #         values = [{'id':str(i+1),'value': value} for i, value in enumerate(values)]
    #         return jsonify(values)
    #     else: 
    #         abort(400, "Invalid table provided")
    # else:

    if table.lower() == 'main_char':
        # Handle main_char separately by combining characters and teams
        characters = db.session.query(series_entities.Character.title).distinct().all()
        teams = db.session.query(series_entities.Team.title).distinct().all()
        
        # Combine results and remove duplicates
        values = {char.title for char in characters} | {team.title for team in teams}
    else:
        table_class = {
            'genre': series_entities.Genre,
            'artist': series_entities.Artist,
            'editor': series_entities.Editor,
            'writer': series_entities.Writer,
            'publisher': series_entities.Publisher,
        }.get(table.lower())

        if table_class is None:
            return jsonify({'error': 'Invalid table name'}), 400

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
    
    # Ensure the list has at least 30 IDs
    while len(series_ids) < 30:
        series_ids.extend(series_ids)
    
    # Randomize the list and select the first 30
    random.shuffle(series_ids)
    series_ids = series_ids[:30]
    
    return jsonify(series_ids)
