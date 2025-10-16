from api import create_app
from waitress import serve
import logging
logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)

def upgrade_database():
    try:
        from alembic.config import main
        main(argv=['upgrade', 'head'])
    except Exception as e:
        print(f"Error while upgrading the database: {e}")

upgrade_database()

app = create_app()

serve(app, host='0.0.0.0', port=6166)