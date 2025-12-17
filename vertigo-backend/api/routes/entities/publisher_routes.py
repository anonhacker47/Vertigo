import os
from flask import jsonify

from flask import Blueprint, abort, request, send_file, send_from_directory
from apifairy import authenticate, response, other_responses
from sqlalchemy import func, or_, select
from api import db
from api.models.series_entities import Publisher
from api.models.issue import Issue

from api.schemas.publisher_schema import PublisherSchema,PublisherDetailSchema

from api.utils.files import get_user_path
from api.utils.auth import token_auth
from api.decorators import paginated_response
from api.schemas.pagination_schema import DateTimePaginationSchema
from api.helpers.thumbnail_processing import download_thumbnail, normalize_thumbnail, save_thumbnail,delete_thumbnail


publisher = Blueprint('publisher', __name__)
publisher_schema = PublisherSchema()
multi_publisher_schema = PublisherSchema(many=True)
update_publisher_schema = PublisherSchema(partial=True)
publisher_thumbs_folder = "Entities/Publisher"

@publisher.route('/publisher', methods=['POST'])
@authenticate(token_auth)
def create_publisher():
    """Create a new publisher"""

    user = token_auth.current_user()

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    thumbnail = request.form.get('thumbnail', '').strip()

    if not title:
        abort(400, description="Title is required")

    publisher = Publisher(
        user=user,
        title=title,
        description=description
    )

    db.session.add(publisher)

    if thumbnail.startswith("http"):

        filename = download_thumbnail(
            thumbnail, title, user.id, publisher_thumbs_folder)
        if filename:
            publisher.thumbnail = filename

    elif 'thumbnail' in request.files:

        file = request.files['thumbnail']
        filename = save_thumbnail(
            file, title, user.id, publisher_thumbs_folder)
        publisher.thumbnail = filename

    db.session.commit()
    return publisher_schema.dump(publisher), 201


@publisher.route('/publisher', methods=['GET'])
@authenticate(token_auth)
@paginated_response(multi_publisher_schema, order_by=Publisher.title,
                    order_direction='asc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all publishers of a user with search enabled"""

    user = token_auth.current_user()
    query_publishers = user.publisher_select() 

    base_total = db.session.scalar(
    select(func.count()).select_from(query_publishers)
    )

    search_query = request.args.get("query", "").strip()
    if search_query:
        query_publishers = query_publishers.filter(
            or_(
                Publisher.title.ilike(f"%{search_query}%"),
                Publisher.description.ilike(f"%{search_query}%")
            )
        )

    return query_publishers, {"base_total": base_total}


@publisher.route('/publisher/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(PublisherDetailSchema)
@other_responses({404: 'Publisher not found'})
def get(id):
    """Retrieve a publisher by id"""
    return db.session.get(Publisher, id) or abort(404)


@publisher.route('publisher/image/<int:id>',methods=['GET'])
def get_publisher_image(id):
    """Retrieve the publisher thumbnail"""
    publisher = db.session.get(Publisher, id)

    user = publisher.user
    user_id = user.id

    if publisher.thumbnail is None:
        return jsonify("noimage")
    
    if publisher is None:
        return jsonify("Publisher not found"), 404
    
    try:    
        base_path = get_user_path(user_id, publisher_thumbs_folder)
        file_path = os.path.join(base_path, publisher.thumbnail)

        return send_file(file_path)
    except FileNotFoundError:
        return jsonify("Image file not found"), 404
    except Exception as e:
        # Handle other potential exceptions (e.g., permission errors)
        return jsonify(f"Error retrieving image: {str(e)}"), 500


@publisher.route('/publisher/<int:id>/neighbours', methods=['GET'])
@authenticate(token_auth)
def neighbors(id):
    """Retrieve the previous and next publisher based on alphabetical order."""

    user = token_auth.current_user()

    publisher_obj = db.session.get(Publisher, id) or abort(404)
    current_title = publisher_obj.title

    prev_publisher = (
        db.session.query(Publisher)
        .filter(Publisher.user_id == user.id, Publisher.title < current_title)
        .order_by(Publisher.title.desc())
        .first()
    )

    next_publisher = (
        db.session.query(Publisher)
        .filter(Publisher.user_id == user.id, Publisher.title > current_title)
        .order_by(Publisher.title.asc())
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
        "previous": format_item(prev_publisher),
        "next": format_item(next_publisher),
    })


@publisher.route('/publisher/<int:id>', methods=['PUT', 'PATCH'])
@authenticate(token_auth)
@response(PublisherDetailSchema)
@other_responses({404: 'Publisher not found'})
def update_publisher(id):
    """Update an existing publisher"""

    user = token_auth.current_user()
    publisher = db.session.get(Publisher, id) or abort(404)

    title = request.form.get('title', '').strip()
    if title:
        publisher.title = title

    description = request.form.get('description', '').strip()
    publisher.description = description or publisher.description

    incoming_thumb = request.form.get('thumbnail', '').strip() if 'thumbnail' in request.form else ''
    old_thumb = publisher.thumbnail
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
                        publisher.title,
                        user.id,
                        publisher_thumbs_folder
                    )

                elif 'thumbnail' in request.files:
                    file = request.files['thumbnail']
                    new_filename = save_thumbnail(
                        file,
                        publisher.title,
                        user.id,
                        publisher_thumbs_folder
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
                delete_thumbnail(old_thumb, user.id, publisher_thumbs_folder)

            publisher.thumbnail = new_filename

    db.session.commit()
    return publisher

@publisher.route('/publisher/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the publisher'})
def delete(id):
    """Delete a publisher"""
    publisher = db.session.get(Publisher, id) or abort(404)
    if publisher.user != token_auth.current_user():
        abort(403)

    db.session.delete(publisher)

    if publisher.thumbnail:
        cover_dir = get_user_path(publisher.user.id, publisher_thumbs_folder)
        file_path = os.path.join(cover_dir, publisher.thumbnail)

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("Thumbnail file does not exist:", file_path)

    db.session.commit()
    return '', 204
