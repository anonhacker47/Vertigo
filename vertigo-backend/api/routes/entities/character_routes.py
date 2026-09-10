from flask import jsonify

from flask import Blueprint, abort, request
from apifairy import authenticate, response, other_responses
from sqlalchemy import func, or_, select
from api import db
from api.models.series_entities import Character
import api.models.series_entities as series_entities

from api.schemas.character_schema import CharacterSchema, CharacterDetailSchema

from api import media
from api.routes.entities.thumbnails import apply_entity_thumbnail
from api.utils.auth import token_auth
from api.decorators import paginated_response
from api.schemas.pagination_schema import DateTimePaginationSchema


character = Blueprint('character', __name__)
character_schema = CharacterSchema()
multi_character_schema = CharacterSchema(many=True)
update_character_schema = CharacterSchema(partial=True)

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
    db.session.flush()  # the thumbnail is stored under the entity's id

    err = apply_entity_thumbnail(character, 'character', user.id)
    if err:
        db.session.rollback()
        return err

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
    if character is None:
        return jsonify("Character not found"), 404
    return media.send(character.user_id, character.thumbnail)
    

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

    err = apply_entity_thumbnail(character, 'character', user.id)
    if err:
        return err

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

    media.remove(character.user_id, character.thumbnail)

    db.session.commit()
    return '', 204