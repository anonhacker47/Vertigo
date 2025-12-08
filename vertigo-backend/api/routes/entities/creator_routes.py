import os
from flask import jsonify

from flask import Blueprint, abort, request, send_file
from apifairy import authenticate, body, response, other_responses
from sqlalchemy import or_
from api import db
from api.models.series_entities import Creator

from api.schemas.creator_schema import CreatorSchema, CreatorDetailSchema

from api.utils.files import get_user_path
from api.utils.auth import token_auth
from api.decorators import paginated_response
from api.schemas.pagination_schema import DateTimePaginationSchema
from api.helpers.thumbnail_processing import download_thumbnail, save_thumbnail,delete_thumbnail


creator = Blueprint('creator', __name__)
creator_schema = CreatorSchema()
multi_creator_schema = CreatorSchema(many=True)
update_creator_schema = CreatorSchema(partial=True)
creator_thumbs_folder = "Entities/Creator"

@creator.route('/creator', methods=['POST'])
@authenticate(token_auth)
def create_creator():
    """Create a new creator"""

    user = token_auth.current_user()

    # Parse form fields
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    thumbnail = request.form.get('thumbnail', '').strip()

    if not title:
        abort(400, description="Title is required")

    # Create creator instance
    creator = Creator(
        user=user,
        title=title,
        description=description
    )

    db.session.add(creator)

    # Thumbnail: URL or file
    if thumbnail.startswith("http"):
        # Thumbnail URL provided
        filename = download_thumbnail(
            thumbnail, title, user.id, creator_thumbs_folder)
        if filename:
            creator.thumbnail = filename

    elif 'thumbnail' in request.files:
        # Thumbnail uploaded as file
        file = request.files['thumbnail']
        filename = save_thumbnail(
            file, title, user.id, creator_thumbs_folder)
        creator.thumbnail = filename

    db.session.commit()
    return creator_schema.dump(creator), 201

@creator.route('/creator', methods=['GET'])
@authenticate(token_auth)
@paginated_response(multi_creator_schema, order_by=Creator.title,
                    order_direction='asc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all creators with search enabled"""

    user = token_auth.current_user()
    qs = user.creator_select() 
    
    search_query = request.args.get("query", "").strip()
    if search_query:
        qs = qs.filter(
            or_(
                Creator.title.ilike(f"%{search_query}%"),
                Creator.description.ilike(f"%{search_query}%")
            )
        )

    return qs

@creator.route('/creator/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(CreatorDetailSchema)
@other_responses({404: 'Creator not found'})
def get(id):
    """Retrieve a creator by id"""
    return db.session.get(Creator, id) or abort(404)

@creator.route('creator/image/<int:id>',methods=['GET'])
def get_creator_image(id):
    """Retrieve the creator thumbnail"""
    creator = db.session.get(Creator, id)

    user = creator.user
    user_id = user.id

    if creator is None:
        return jsonify("Creator not found"), 404

    if creator.thumbnail is None:
        return jsonify("noimage")

    try:
        base_path = get_user_path(user_id, creator_thumbs_folder)
        file_path = os.path.join(base_path, creator.thumbnail)
        
        return send_file(file_path)
    except FileNotFoundError:
        return jsonify("Image file not found"), 404
    except Exception as e:
        # Handle other potential exceptions (e.g., permission errors)
        return jsonify(f"Error retrieving image: {str(e)}"), 500

@creator.route('/creator/<int:id>/neighbours', methods=['GET'])
@authenticate(token_auth)
def neighbors(id):
    """Retrieve the previous and next creator based on alphabetical order."""

    user = token_auth.current_user()

    creator_obj = db.session.get(Creator, id) or abort(404)
    current_title = creator_obj.title

    prev_creator = (
        db.session.query(Creator)
        .filter(Creator.user_id == user.id, Creator.title < current_title)
        .order_by(Creator.title.desc())
        .first()
    )

    next_creator = (
        db.session.query(Creator)
        .filter(Creator.user_id == user.id, Creator.title > current_title)
        .order_by(Creator.title.asc())
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
        "previous": format_item(prev_creator),
        "next": format_item(next_creator),
    })

@creator.route('/creator/<int:id>', methods=['PUT', 'PATCH'])
@authenticate(token_auth)
@response(CreatorDetailSchema)
@other_responses({404: 'Creator not found'})
def update_creator(id):
    """Update an existing creator"""

    user = token_auth.current_user()
    creator = db.session.get(Creator, id) or abort(404)

    # Update title
    title = request.form.get('title', '').strip()
    if title:
        creator.title = title

    # Update description
    description = request.form.get('description', '').strip()
    creator.description = description or creator.description

    incoming_thumb = request.form.get('thumbnail', '').strip() if 'thumbnail' in request.form else ''
    old_thumb = creator.thumbnail
    new_filename = None
    error_occurred = False

    if incoming_thumb or 'thumbnail' in request.files:

        if incoming_thumb == old_thumb:
            new_filename = None

        else:
            try:
                if incoming_thumb.startswith('http'):
                    new_filename = download_thumbnail(
                        incoming_thumb,
                        creator.title,
                        user.id,
                        creator_thumbs_folder
                    )

                elif 'thumbnail' in request.files:
                    file = request.files['thumbnail']
                    new_filename = save_thumbnail(
                        file,
                        creator.title,
                        user.id,
                        creator_thumbs_folder
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

            # If thumbnail is changing, delete old file
            if new_filename is not None and old_thumb:
                delete_thumbnail(old_thumb, user.id, creator_thumbs_folder)

            # Apply updated or cleared thumbnail
            creator.thumbnail = new_filename

    db.session.commit()
    return creator

@creator.route('/creator/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the creator'})
def delete(id):
    """Delete a creator"""
    creator = db.session.get(Creator, id) or abort(404)
    if creator.user != token_auth.current_user():
        abort(403)

    db.session.delete(creator)

    if creator.thumbnail:
        cover_dir = get_user_path(creator.user.id, creator_thumbs_folder)
        file_path = os.path.join(cover_dir, creator.thumbnail)

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("Thumbnail file does not exist:", file_path)

    db.session.commit()
    return '', 204
