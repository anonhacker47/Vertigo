import os
from pstats import SortKey
import random
from flask import current_app, json, jsonify
import sqlite3

from flask import Blueprint, abort, request, send_file, send_from_directory
from apifairy import authenticate, body, response, other_responses
from sqlalchemy import func, or_, select
from api import db
from api.models.user import User
from api.models.series_entities import Character
import api.models.series_entities as series_entities
from api.models.issue import Issue

from api.schemas.character_schema import CharacterSchema, CharacterDetailSchema
from api.schemas.empty_schema import EmptySchema

from api.utils.files import get_user_path
from api.utils.auth import token_auth
from api.decorators import paginated_response
from api.schemas.pagination_schema import DateTimePaginationSchema
from api.helpers.thumbnail_processing import download_thumbnail, save_thumbnail,delete_thumbnail


character = Blueprint('character', __name__)
character_schema = CharacterSchema()
multi_character_schema = CharacterSchema(many=True)
update_character_schema = CharacterSchema(partial=True)
character_thumbs_folder = "Entities/Character"

@character.route('/character', methods=['POST'])
@authenticate(token_auth)
def create_character():
    """Create a new character"""

    user = token_auth.current_user()

    # Parse form fields
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    thumbnail = request.form.get('thumbnail', '').strip()

    if not title:
        abort(400, description="Title is required")

    # Create character instance
    character = Character(
        user=user,
        title=title,
        description=description
    )

    db.session.add(character)

    # Thumbnail: URL or file
    if thumbnail.startswith("http"):
        # Thumbnail URL provided
        filename = download_thumbnail(
            thumbnail, title, user.id, character_thumbs_folder)
        if filename:
            character.thumbnail = filename

    elif 'thumbnail' in request.files:
        # Thumbnail uploaded as file
        file = request.files['thumbnail']
        filename = save_thumbnail(
            file, title, user.id, character_thumbs_folder)
        character.thumbnail = filename

    db.session.commit()
    return character_schema.dump(character), 201


@character.route('/character', methods=['GET'])
@authenticate(token_auth)
@paginated_response(multi_character_schema, order_by=Character.title,
                    order_direction='asc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all characters of a user with search enabled"""
    
    user = token_auth.current_user()
    qc = user.character_select() 
    
    base_total = db.session.scalar(
    select(func.count()).select_from(qc)
    )

    search_query = request.args.get("query", "").strip()
    if search_query:
        qc = qc.filter(
            or_(
                Character.title.ilike(f"%{search_query}%"),
                Character.description.ilike(f"%{search_query}%")
            )
        )

    return qc, {"base_total": base_total}


@character.route('/character/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(CharacterDetailSchema)
@other_responses({404: 'Character not found'})
def get(id):
    """Retrieve a character by id"""
    return db.session.get(Character, id) or abort(404)


@character.route('character/image/<int:id>',methods=['GET'])
def get_character_image(id):
    """Retrieve the character thumbnail"""
    character = db.session.get(Character, id)

    user = character.user
    user_id = user.id

    if character is None:
        return jsonify("Character not found"), 404

    if character.thumbnail is None:
        return jsonify("noimage")

    try:
        base_path = get_user_path(user_id, character_thumbs_folder)
        file_path = os.path.join(base_path, character.thumbnail)
        
        return send_file(file_path)
    except FileNotFoundError:
        return jsonify("Image file not found"), 404
    except Exception as e:
        # Handle other potential exceptions (e.g., permission errors)
        return jsonify(f"Error retrieving image: {str(e)}"), 500
    

@character.route('/character/<int:id>/neighbours', methods=['GET'])
@authenticate(token_auth)
def neighbors(id):
    """Retrieve the previous and next character based on alphabetical order."""

    user = token_auth.current_user()

    character_obj = db.session.get(Character, id) or abort(404)
    current_title = character_obj.title

    prev_character = (
        db.session.query(Character)
        .filter(Character.user_id == user.id, Character.title < current_title)
        .order_by(Character.title.desc())
        .first()
    )

    next_character = (
        db.session.query(Character)
        .filter(Character.user_id == user.id, Character.title > current_title)
        .order_by(Character.title.asc())
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
        "previous": format_item(prev_character),
        "next": format_item(next_character),
    })


@character.route('/character/<int:id>', methods=['PUT', 'PATCH'])
@authenticate(token_auth)
@response(CharacterDetailSchema)
@other_responses({404: 'Character not found'})
def update_character(id):
    """Update an existing character"""

    user = token_auth.current_user()
    character = db.session.get(Character, id) or abort(404)

    title = request.form.get('title', '').strip()
    if title:
        character.title = title

    description = request.form.get('description', '').strip()
    character.description = description or character.description

    incoming_thumb = request.form.get('thumbnail', '').strip() if 'thumbnail' in request.form else ''
    old_thumb = character.thumbnail
    new_filename = None
    error_occurred = False

    if incoming_thumb or 'thumbnail' in request.files:

        if incoming_thumb and incoming_thumb.__contains__("/api/"):
            new_filename = None

        else:
            try:
                if incoming_thumb.startswith('http'):
                    new_filename = download_thumbnail(
                        incoming_thumb,
                        character.title,
                        user.id,
                        character_thumbs_folder
                    )

                elif 'thumbnail' in request.files:
                    file = request.files['thumbnail']
                    new_filename = save_thumbnail(
                        file,
                        character.title,
                        user.id,
                        character_thumbs_folder
                    )

                elif incoming_thumb == "":
                    new_filename = None

                if new_filename is False:
                    error_occurred = True

            except Exception as e:
                print("Thumbnail update failed:", e)
                error_occurred = True

            if error_occurred:
                return jsonify({"error": "Failed to update thumbnail"}), 400

            if new_filename is not None and old_thumb:
                delete_thumbnail(old_thumb, user.id, character_thumbs_folder)

            character.thumbnail = new_filename

    db.session.commit()
    return character

@character.route('/character/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the creator'})
def delete(id):
    """Delete a creator"""
    character = db.session.get(Character, id) or abort(404)
    if character.user != token_auth.current_user():
        abort(403)

    db.session.delete(character)

    if character.thumbnail:
        cover_dir = get_user_path(character.user.id, character_thumbs_folder)
        file_path = os.path.join(cover_dir, character.thumbnail)

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("Thumbnail file does not exist:", file_path)

    db.session.commit()
    return '', 204