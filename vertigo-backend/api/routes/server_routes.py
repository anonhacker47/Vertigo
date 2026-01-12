from flask import Blueprint, current_app, jsonify
from flask_marshmallow import Marshmallow
from apifairy import response, other_responses 
from marshmallow import fields     
from api.models.series import Series
from api.models.issue import Issue
from api.schemas.series_schema import SeriesSchema
from api.schemas.issue_schema import IssueSchema
from api.schemas.genre_schema import GenreSchema
from api.schemas.character_schema import CharacterSchema
from api.schemas.publisher_schema import PublisherSchema
from api.schemas.creator_schema import CreatorSchema
from apifairy import authenticate
from api.utils.auth import token_auth
from api.models.series_entities import Genre, Publisher, Creator, Character
from api import db


server = Blueprint('server', __name__)

ma = Marshmallow()

class PingResponseSchema(ma.Schema):
    status = fields.String(required=True,)
    message = fields.String(required=True)
    version = fields.String(required=True)

@server.route('/ping', methods=['GET'])
@response(PingResponseSchema, description="Health check response")
@other_responses({404: {'description': 'Server not reachable'}})
def ping():
    """Health check route"""
    return {'status': 'ok', 'message': 'Server is running','version': current_app.config['SERVER_VERSION']}, 200

series_schema = SeriesSchema(many=True)
issue_schema = IssueSchema(many=True)
genre_schema = GenreSchema(many=True)
publisher_schema = PublisherSchema(many=True)
creator_schema = CreatorSchema(many=True)
character_schema = CharacterSchema(many=True)

@server.route('/sync/full', methods=['GET'])
@authenticate(token_auth)
def full_sync():
    """Return all relevant data for background sync"""
    user = token_auth.current_user()
    user_id = user.id if user else None

    # Series and issues
    series = db.session.query(Series).filter_by(user_id=user_id).all()
    issues = db.session.query(Issue).join(Series).filter(Series.user_id == user_id).all()

    # Related global data
    genres = db.session.query(Genre).all()
    publishers = db.session.query(Publisher).all()
    creators = db.session.query(Creator).all()
    characters = db.session.query(Character).all()

    return jsonify({
        "series": series_schema.dump(series),
        "issues": issue_schema.dump(issues),
        "genres": genre_schema.dump(genres),
        "publishers": publisher_schema.dump(publishers),
        "creators": creator_schema.dump(creators),
        "characters": character_schema.dump(characters),
    })