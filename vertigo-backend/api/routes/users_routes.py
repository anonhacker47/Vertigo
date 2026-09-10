from apifairy.decorators import other_responses
from flask import Blueprint, abort, jsonify, request, send_file
from apifairy import authenticate, body, response

import sqlalchemy as sqla
from api import db
from api.models.user import User
from api.models.series import Series
from api import media
import pandas as pd
from io import BytesIO
from flask import send_file
from api.schemas.user_schema import UserSchema, UpdateUserSchema
from sqlalchemy.orm import selectinload

from api.utils.auth import token_auth

from api.helpers.excel_processing import create_stats_sheet, format_series_sheet, format_issues_sheet
from babel.numbers import get_currency_symbol
from api.models.series_entities import Character, Creator, Genre, Publisher

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

    # Profile picture: file, URL or "noimage"; the previous file is replaced.
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
   


@users.route('/export_data', methods=['GET'])
@authenticate(token_auth)
def export_data():
    """Export user data"""
    user = token_auth.current_user()
    
    # Fetch user's series
    series_stmt = user.series_select().options(selectinload(Series.issue))
    series_list = db.session.execute(series_stmt).scalars().all()   
    
    def resolve_cover(value):
        return media.resolve(user.id, value)

    # Prepare data for DataFrame
    series_data = []
    issues_data = []

    currency_code = user.preferred_currency  # e.g., 'USD', 'INR', etc.
    currency_symbol = get_currency_symbol(currency_code)
    purchase_field = f"Purchase Cost ({currency_symbol})"

    for s in series_list:
        missing_issues = [str(i.number) for i in s.issue if not i.is_owned]
        series_data.append({
            "Thumbnail": s.thumbnail,
            "Series Title": s.title,
            "Publisher": ", ".join(p.title for p in s.publisher),
            "Genre": ", ".join(g.title for g in s.genre),
            "Creators": ", ".join(c.title for c in s.creator),
            "Description": s.description,
            "Issue Count": s.issue_count,
            "Owned Count": f"{s.owned_count} / {s.issue_count}",
            "Missing Issues": ", ".join(missing_issues) if missing_issues else "None",
            "Read Count": f"{s.read_count} / {s.issue_count}",
            "Rating": s.user_rating,
            purchase_field: s.purchase_cost,
        })

        for i in s.issue:
            issues_data.append({
                "Series Title": s.title,
                "Issue Number": i.number,
                "Owned Already?": "Yes" if i.is_owned else "No",
                "Read Already?": "Yes" if i.is_read else "No",
                "Bought Price": i.bought_price,
                "Bought Date": i.bought_date,
                "Read Date": i.read_date,
            })


    # Step 2: Create Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_series = pd.DataFrame(series_data)
        df_issues = pd.DataFrame(issues_data)

        # Write dataframes
        df_series.to_excel(writer, index=False, sheet_name='Series')
        df_issues.to_excel(writer, index=False, sheet_name='Issues')

        # Apply formatting only if data exists
        if not df_series.empty:
            format_series_sheet(writer.book['Series'], df_series, resolve_cover)
        if not df_issues.empty:
            format_issues_sheet(writer.book['Issues'], df_issues)
            
        create_stats_sheet(writer.book, df_series, df_issues)

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=f"comic_export_user_{user.id}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@users.route('/delete_all_data', methods=['DELETE'])
@authenticate(token_auth)
def delete_all_user_data():
    user = token_auth.current_user()
    deleted_counts = {}

    # --- DELETE SERIES ---
    series_stmt = user.series_select().options(selectinload(Series.issue))
    series_list = db.session.execute(series_stmt).scalars().all()

    for s in series_list:
        db.session.delete(s)

    deleted_counts["series"] = len(series_list)

    # --- DELETE ENTITIES ---
    entity_models = [Publisher, Character, Creator, Genre]

    for model in entity_models:
        stmt = sqla.select(model).filter_by(user_id=user.id)
        items = db.session.execute(stmt).scalars().all()

        for item in items:
            db.session.delete(item)

        deleted_counts[model.__tablename__] = len(items)
    media.delete_user_media(user.id, keep_avatar=True)
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
