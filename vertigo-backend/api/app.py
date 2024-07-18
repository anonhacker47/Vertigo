import os
from pydoc import render_doc
from flask import Flask, redirect, url_for, request, render_template
from alchemical.flask import Alchemical
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_mail import Mail
from apifairy import APIFairy
from config import Config

db = Alchemical()
ma = Marshmallow()
cors = CORS()
mail = Mail()
apifairy = APIFairy()


def create_app(config_class=Config):
    app = Flask(__name__,
            static_folder = "./wwwroot/static",
            template_folder = "./wwwroot")
    app.config.from_object(config_class)
    
    app.config['cover_path'] = os.path.abspath("./Config/Covers/")
    app.config['sql_path'] = os.path.abspath("./Config/")

    # Check if 'sql_path' exists and create it if not
    if not os.path.exists(app.config['sql_path']):
        os.makedirs(app.config['sql_path'])
        print("The 'sql_path' directory is created!")    

    # Check if 'cover_path' exists and create it if not
    if not os.path.exists(app.config['cover_path']):
        os.makedirs(app.config['cover_path'])
        print("The 'cover_path' directory is created!")    

    # extensions
    from api import models
    db.init_app(app)
    ma.init_app(app)
    if app.config['USE_CORS']:  # pragma: no branch
        cors.init_app(app)
    mail.init_app(app)
    apifairy.init_app(app)

    # blueprints
    from api.errors import errors
    app.register_blueprint(errors)
    from api.tokens import tokens
    app.register_blueprint(tokens, url_prefix='/api')
    from api.users import users
    app.register_blueprint(users, url_prefix='/api')
    from api.series import series
    app.register_blueprint(series, url_prefix='/api') 
    from api.issue import issues
    app.register_blueprint(issues, url_prefix='/api') 
    from api.dashboard import dashboard
    app.register_blueprint(dashboard, url_prefix='/api') 

    # define the shell context
    @app.shell_context_processor
    def shell_context():  # pragma: no cover
        ctx = {'db': db}
        for attr in dir(models):
            model = getattr(models, attr)
            if hasattr(model, '__bases__') and \
                    db.Model in getattr(model, '__bases__'):
                ctx[attr] = model
        return ctx

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):
        return render_template('index.html')
    
    @app.route('/api/docs')
    def docs():  # pragma: no cover
        return redirect(url_for('apifairy.docs'))

    @app.after_request
    def after_request(response):
        # Werkzeug sometimes does not flush the request body so we do it here
        request.get_data()
        return response

    return app