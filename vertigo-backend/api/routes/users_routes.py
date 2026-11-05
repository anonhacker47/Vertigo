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
users_schema = UserSchema(many=True)
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


# @users.route('/users', methods=['GET'])
# @authenticate(token_auth)
# @paginated_response(users_schema)
# def all():
#     """Retrieve all users"""
#     return User.select()


@users.route('/users/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get(id):
    """Retrieve a user by id"""
    return db.session.get(User, id) or abort(404)


# @users.route('/users/<username>', methods=['GET'])
# @authenticate(token_auth)
# @response(user_schema)
# @other_responses({404: 'User not found'})
# def get_by_username(username):
#     """Retrieve a user by username"""
#     return db.session.scalar(User.select().filter_by(username=username)) or \
#         abort(404)


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

@users.route('me/profile-picture/',methods=['GET'])
@authenticate(token_auth)
def get_profile_picture():
    """Retrieve the User profile picture"""
    user = token_auth.current_user()

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


# @users.route('/me/following', methods=['GET'])
# @authenticate(token_auth)
# @paginated_response(users_schema, order_by=User.username)
# def my_following():
#     """Retrieve the users the logged in user is following"""
#     user = token_auth.current_user()
#     return user.following_select()


# @users.route('/me/followers', methods=['GET'])
# @authenticate(token_auth)
# @paginated_response(users_schema, order_by=User.username)
# def my_followers():
#     """Retrieve the followers of the logged in user"""
#     user = token_auth.current_user()
#     return user.followers_select()


# @users.route('/me/following/<int:id>', methods=['GET'])
# @authenticate(token_auth)
# @response(EmptySchema, status_code=204,
#           description='User is followed.')
# @other_responses({404: 'User is not followed'})
# def is_followed(id):
#     """Check if a user is followed"""
#     user = token_auth.current_user()
#     followed_user = db.session.get(User, id) or abort(404)
#     if not user.is_following(followed_user):
#         abort(404)
#     return {}


# @users.route('/me/following/<int:id>', methods=['POST'])
# @authenticate(token_auth)
# @response(EmptySchema, status_code=204,
#           description='User followed successfully.')
# @other_responses({404: 'User not found', 409: 'User already followed.'})
# def follow(id):
#     """Follow a user"""
#     user = token_auth.current_user()
#     followed_user = db.session.get(User, id) or abort(404)
#     if user.is_following(followed_user):
#         abort(409)
#     user.follow(followed_user)
#     db.session.commit()
#     return {}


# @users.route('/me/following/<int:id>', methods=['DELETE'])
# @authenticate(token_auth)
# @response(EmptySchema, status_code=204,
#           description='User unfollowed successfully.')
# @other_responses({404: 'User not found', 409: 'User is not followed.'})
# def unfollow(id):
#     """Unfollow a user"""
#     user = token_auth.current_user()
#     unfollowed_user = db.session.get(User, id) or abort(404)
#     if not user.is_following(unfollowed_user):
#         abort(409)
#     user.unfollow(unfollowed_user)
#     db.session.commit()
#     return {}


# @users.route('/users/<int:id>/following', methods=['GET'])
# @authenticate(token_auth)
# @paginated_response(users_schema, order_by=User.username)
# @other_responses({404: 'User not found'})
# def following(id):
#     """Retrieve the users this user is following"""
#     user = db.session.get(User, id) or abort(404)
#     return user.following_select()


# @users.route('/users/<int:id>/followers', methods=['GET'])
# @authenticate(token_auth)
# @paginated_response(users_schema, order_by=User.username)
# @other_responses({404: 'User not found'})
# def followers(id):
#     """Retrieve the followers of the user"""
#     user = db.session.get(User, id) or abort(404)
#     return user.followers_select()
