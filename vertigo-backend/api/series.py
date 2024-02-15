import os
from pstats import SortKey
from flask import current_app, jsonify
import sqlite3

from flask import Blueprint, abort, request, send_file, send_from_directory
from apifairy import authenticate, body, response, other_responses

from api import db
from api.models import User, Series, Issue
from api.schemas import SeriesSchema, EmptySchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import DateTimePaginationSchema


series = Blueprint('series', __name__)
series_schema = SeriesSchema()
multi_series_schema = SeriesSchema(many=True)
update_series_schema = SeriesSchema(partial=True)

@series.route('/series', methods=['POST'])
@authenticate(token_auth)
@body(series_schema)
@response(series_schema, 201)
def new(args):
    """Create a new series"""
    user = token_auth.current_user()
    series = Series(user=user, **args)
    db.session.add(series)
    db.session.commit()
    return series


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
@body(update_series_schema)
@response(series_schema)
@other_responses({403: 'Not allowed to edit this series',
                  404: 'Series not found'})
def put(data, id):
    """Edit a series"""
    series = db.session.get(Series, id) or abort(404)
    if series.user != token_auth.current_user():
        abort(403)
    series.update(data)
    db.session.commit()
    return series


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
        print(issue.id)
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
def getSeriesImage(id):
    """Retrieve the series thumbnail"""
    series = db.session.get(Series, id)
    if series.thumbnail == "noimage":
        return jsonify("noimage")
    else:
        return send_file(current_app.config['cover_path']+f"\\{series.thumbnail}")

@series.route('/series/key', methods=['GET'])
@authenticate(token_auth)
def key():
    """Retrieve series key"""
    obj = db.session.query(Series).order_by(Series.id.desc()).first()
    if obj is None:
        return jsonify("0")
    else:
        return jsonify(f"{obj.id}")
    
@series.route('/series/filter/<field>', methods=['GET'])
# @authenticate(token_auth)
# @response(200)
def get_series_by_field(field):
    """Retrieve values from a specific field across all series objects."""
    if field not in ['title', 'publisher', 'genre', 'main_char', 'writer', 'artist', 'editor', 'summary']:
        abort(400, "Invalid field provided")

    # Get all series objects
    values = db.session.query(getattr(Series, field)).distinct().all()

    # Extract the desired field values
    values = [value[0] for value in values if value[0]]

    # Remove duplicates (optional)
    values = list(set(values))
    values.sort() 
    print(values)

    return jsonify(values)