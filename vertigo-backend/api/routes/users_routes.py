from apifairy.decorators import other_responses
from flask import Blueprint, abort, jsonify, request
from apifairy import authenticate, body, response

from api import db
from api.models.user import User
from api import media
from api.schemas.user_schema import UserSchema, UpdateUserSchema
from api.schemas.shelf_schema import ShelfSettingsSchema, shelf_settings
from api.models.series_entities import Character, Publisher

from api.utils.auth import token_auth
from api.utils.collection import delete_collection

users = Blueprint('users', __name__)
user_schema = UserSchema()
update_user_schema = UpdateUserSchema(partial=True)
shelf_settings_schema = ShelfSettingsSchema()


@users.route('/users', methods=['POST'])
@body(user_schema)
@response(user_schema, 201)
def new(args):
    """Register a new user"""
    user = User(**args)
    db.session.add(user)
    db.session.commit()
    media.init_user_dirs(user.id)
    return user


@users.route('/users/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get(id):
    """Retrieve a user by id; only your own"""
    user = token_auth.current_user()
    if id != user.id:
        abort(404)
    return user


@users.route('/me', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
def me():
    """Retrieve the authenticated user"""
    return token_auth.current_user()


@users.route('/me', methods=['PUT'])
@authenticate(token_auth)
# @body(update_user_schema)
@response(user_schema)
def put():
    """Edit user information (multipart/form-data supported)"""
    user = token_auth.current_user()
    form = request.form


    if 'username' in form:
        username = form.get('username', '').strip()
        if len(username) < 3 or len(username) > 64 or not username[0].isalpha():
            abort(400, description="Username must be 3 to 64 characters and start with a letter.")
        if username != user.username and \
                db.session.scalar(User.select().filter_by(username=username)):
            abort(400, description=f"The username '{username}' is already taken.")
        user.username = username
    if 'email' in form:
        email = form.get('email', '').strip()
        if '@' not in email or len(email) > 120:
            abort(400, description="Enter a valid email address.")
        if email != user.email and \
                db.session.scalar(User.select().filter_by(email=email)):
            abort(400, description=f"The email '{email}' is already in use.")
        user.email = email
    if 'preferred_currency' in form:
        currency = form.get('preferred_currency').strip().upper()
        if len(currency) != 3 or not currency.isalpha():
            abort(400, description="Invalid currency code")
        user.preferred_currency = currency

    if 'password' in form:
        if 'old_password' not in form or not user.verify_password(form.get('old_password')):
            abort(400, description="Old password missing or incorrect")
        user.password = form.get('password')

    try:
        state, relpath, _ = media.apply_thumbnail_field(
            user.id, form, request.files, 'profile_picture',
            rel_dir=media.AVATAR_DIR, filename='avatar',
            current=user.profile_picture,
        )
    except media.MediaError as e:
        abort(400, description=f"Failed to save profile picture: {e}")
    if state == 'set':
        user.profile_picture = relpath
    elif state == 'cleared':
        user.profile_picture = None

    db.session.commit()
    return user

@users.route('/users/<int:id>/avatar', methods=['GET'])
def get_avatar(id):
    """Retrieve the user's avatar (JSON "noimage" when there is none)"""
    user = db.session.get(User, id)
    if user is None:
        return jsonify("User not found"), 404
    return media.send(user.id, user.profile_picture)



@users.route('/me/shelf', methods=['GET'])
@authenticate(token_auth)
@response(shelf_settings_schema)
def get_shelf():
    """How the 3D shelf is arranged"""
    return shelf_settings(token_auth.current_user())


@users.route('/me/shelf', methods=['PUT'])
@authenticate(token_auth)
@body(shelf_settings_schema)
@response(shelf_settings_schema)
def put_shelf(args):
    """Arrange the 3D shelf: its standees, order and what it shelves"""
    user = token_auth.current_user()
    if args['standees'] is not None:
        ids = list(dict.fromkeys(args['standees']))
        owned = db.session.scalars(user.character_select().filter(Character.id.in_(ids))).all() if ids else []
        if len(owned) != len(ids):
            abort(400, description="Pick characters from your own collection.")
        args['standees'] = ids
    if args['publisher'] is not None and not db.session.scalar(
            user.publisher_select().filter(Publisher.id == args['publisher'])):
        abort(400, description="Pick a publisher from your own collection.")
    user.shelf_settings = args
    db.session.commit()
    return args


@users.route('/delete_all_data', methods=['DELETE'])
@authenticate(token_auth)
def delete_all_user_data():
    """Delete every series, issue and entity of the current user; the account stays."""
    user = token_auth.current_user()
    deleted_counts = delete_collection(user)
    db.session.commit()

    return jsonify({
        "message": "Deleted user data.",
        "deleted": deleted_counts
    }), 200
