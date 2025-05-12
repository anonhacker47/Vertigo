from apifairy.decorators import other_responses
from flask import Blueprint, abort, current_app, jsonify,request, send_file
from apifairy import authenticate, body, response

from api import db
from api.models.user import User
from api.schemas.user_schema import UserSchema, UpdateUserSchema
from api.schemas.empty_schema import EmptySchema

from api.utils.auth import token_auth
from api.helpers.thumbnail_processing import download_series_thumbnail, save_series_thumbnail,delete_series_thumbnail

users = Blueprint('users', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema(partial=True)


@users.route('/users', methods=['POST'])
@body(user_schema)
@response(user_schema, 201)
def new(args):
    """Register a new user"""
    user = User(**args)
    db.session.add(user)
    db.session.commit()
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

    # Text field updates
    if 'username' in form:
        user.username = form.get('username').strip()
    if 'email' in form:
        user.email = form.get('email').strip()
    if 'preferred_currency' in form:
        currency = form.get('preferred_currency').strip().upper()
        if len(currency) != 3 or not currency.isalpha():
            abort(400, description="Invalid currency code")
        user.preferred_currency = currency

    # Handle password change
    if 'password' in form:
        if 'old_password' not in form or not user.verify_password(form.get('old_password')):
            abort(400, description="Old password missing or incorrect")
        user.password = form.get('password')

    # Handle profile picture
    profile_picture = form.get('profile_picture', '').strip() if 'profile_picture' in form else ''
    if profile_picture.startswith('http'):
        picture_filename = download_series_thumbnail(profile_picture, user.username,'user_path')
        if picture_filename:
            user.profile_picture = picture_filename
    elif 'profile_picture' in request.files:
        file = request.files['profile_picture']
        picture_filename = save_series_thumbnail(file, user.username,'user_path')
        if picture_filename:
            user.profile_picture = picture_filename

    db.session.commit()
    return user

@users.route('me/profile-picture/',methods=['GET'])
@authenticate(token_auth)
def get_profile_picture():
    """Retrieve the User profile picture"""
    user = token_auth.current_user()

    if user is None:
        return jsonify("User not found"), 404

    if user.profile_picture is None:
        return jsonify("noimage")

    try:
        return send_file(current_app.config['user_path'] + f"\\{user.profile_picture}")
    except FileNotFoundError:
        return jsonify("Image file not found"), 404
    except Exception as e:
        # Handle other potential exceptions (e.g., permission errors)
        return jsonify(f"Error retrieving image: {str(e)}"), 500
   


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
