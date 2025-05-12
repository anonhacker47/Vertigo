from run import app
from waitress import serve
import logging
logger = logging.getLogger('gunicorn')
logger.setLevel(logging.DEBUG)

def upgrade_database():
    try:
        from alembic.config import main
        main(argv=['upgrade', 'head'])
    except Exception as e:
        print(f"Error while upgrading the database: {e}")


upgrade_database()

serve(app, host='0.0.0.0', port=6166)