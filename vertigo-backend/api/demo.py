from flask import abort, current_app, request

MESSAGE = "This demo is read-only."
READ_METHODS = ('GET', 'HEAD', 'OPTIONS')
# sign-in must keep working
OPEN_BLUEPRINTS = ('tokens',)
# external lookups would spend the server's API quota
CLOSED_BLUEPRINTS = ('mokkari', 'tenrai')


def register(app):
    @app.before_request
    def read_only_guard():
        if not current_app.config.get('DEMO_MODE') or not request.path.startswith('/api/'):
            return
        if request.method == 'OPTIONS' or request.blueprint in OPEN_BLUEPRINTS:
            return
        if request.blueprint in CLOSED_BLUEPRINTS or request.method not in READ_METHODS:
            abort(403, MESSAGE)
