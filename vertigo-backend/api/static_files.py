import mimetypes
import os

from flask import current_app, request, send_file
from werkzeug.security import safe_join

# precompressed siblings written by the frontend build, best first
ENCODINGS = (("br", ".br"), ("gzip", ".gz"))
YEAR = 31536000


def wwwroot():
    return current_app.config.get('WWWROOT') or os.path.join(current_app.root_path, 'wwwroot')


def send(root, path, immutable=False):
    """The file, or its precompressed sibling when the client accepts one; None if missing."""
    full = safe_join(root, path)
    if not full or not os.path.isfile(full):
        return None
    max_age = YEAR if immutable else None
    response = None
    for name, ext in ENCODINGS:
        if request.accept_encodings.quality(name) > 0 and os.path.isfile(full + ext):
            response = send_file(full + ext, mimetype=mimetypes.guess_type(full)[0],
                                 max_age=max_age)
            response.content_encoding = name
            break
    if response is None:
        response = send_file(full, max_age=max_age)
    response.vary.add('Accept-Encoding')
    if immutable:
        response.cache_control.immutable = True
    return response


def register(app):
    @app.route('/static/<path:path>')
    def static(path):
        # names are content-hashed by the build
        return send(os.path.join(wwwroot(), 'static'), path, immutable=True) or ("Not found", 404)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):
        if path.startswith("api"):
            return "Not found", 404
        root = wwwroot()
        if path:
            found = send(root, path) or send(os.path.join(root, 'static'), path)
            if found:
                return found
            if path == 'favicon.ico':
                return '', 204
        return send(root, 'index.html') or ("Not found", 404)
