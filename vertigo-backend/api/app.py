import os
from pydoc import render_doc
from flask import Flask, redirect, send_file, send_from_directory, url_for, request, render_template
from alchemical.flask import Alchemical
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_mail import Mail
from apifairy import APIFairy
from config import Config
import importlib.util

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
   
    app.config['user_path'] = os.path.abspath("./Config/User/")
    app.config['sql_path'] = os.path.abspath("./Config/")

    # Check if 'sql_path' exists and create it if not
    if not os.path.exists(app.config['sql_path']):
        os.makedirs(app.config['sql_path'])
        print("The 'sql_path' directory is created!")    

    # Check if 'cover_path' exists and create it if not
    if not os.path.exists(app.config['user_path']):
        os.makedirs(app.config['user_path'])
        print("The 'User' directory is created!")  

    # extensions
    from api import models  

    db.init_app(app)
    ma.init_app(app)
    if app.config['USE_CORS']:  # pragma: no branch
        cors.init_app(app,resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}},
        supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', False)
    )
    mail.init_app(app)
    apifairy.init_app(app)

    # blueprints
    if importlib.util.find_spec("api.fake"):
        from api.fake import fake
        app.register_blueprint(fake)

    from api.errors import errors
    app.register_blueprint(errors)
    from api.routes.tokens_routes import tokens
    app.register_blueprint(tokens, url_prefix='/api')
    from api.routes.users_routes import users
    app.register_blueprint(users, url_prefix='/api')
    from api.routes.series_routes import series
    app.register_blueprint(series, url_prefix='/api') 
    from api.routes.issue_routes import issues
    app.register_blueprint(issues, url_prefix='/api') 
    from api.routes.dashboard_routes import dashboard
    app.register_blueprint(dashboard, url_prefix='/api') 

    from api.routes.entities.publisher_routes import publisher
    app.register_blueprint(publisher, url_prefix='/api')
    from api.routes.entities.creator_routes import creator
    app.register_blueprint(creator, url_prefix='/api')
    from api.routes.entities.character_routes import character
    app.register_blueprint(character, url_prefix='/api')

    #integrations
    from api.integrations.mokkari.mokkari_routes import mokkari
    app.register_blueprint(mokkari, url_prefix='/api')

    from api.integrations.jikan.jikan_routes import jikan
    app.register_blueprint(jikan, url_prefix='/api')

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
        if path.startswith("api"):
            return "Not found", 404

        full_path = os.path.join(app.static_folder, path)
        if os.path.exists(full_path) and not os.path.isdir(full_path):
            return send_from_directory(app.static_folder, path)

        return render_template('index.html')
    
    @app.route('/favicon.ico')
    def favicon():
        try:
            # Absolute path to the favicon
            favicon_path = os.path.join(app.root_path, 'wwwroot', 'favicon.ico')
    
            if not os.path.exists(favicon_path):
                print(f"⚠️ favicon.ico not found at {favicon_path}")
                return '', 204  # No Content if missing
    
            return send_file(favicon_path, mimetype='image/vnd.microsoft.icon')
    
        except Exception as e:
            print(f"⚠️ Error serving favicon.ico: {e}")
            return '', 204  # Prevent 500 JSON
    
    @app.route('/api/docs')
    def docs():  # pragma: no cover
        return redirect(url_for('apifairy.docs'))

    @app.after_request
    def after_request(response):
        # Werkzeug sometimes does not flush the request body so we do it here
        request.get_data()
        return response

    from api.integrations.mokkari.task_queue import start_mokkari_workers
    start_mokkari_workers(app, num_workers=1)

    return app