from api import create_app
from waitress import serve
import logging
import os
import sys
logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

def upgrade_database():
    try:
        from alembic.config import main
        main(argv=['upgrade', 'head'])
    except Exception as e:
        print(f"Error while upgrading the database: {e}")

upgrade_database()

app = create_app()

def migrate_media_layout():
    """Idempotent: moves images from the legacy Config/User layout on first run."""
    try:
        from api.media_migrate import migrate_media
        with app.app_context():
            migrate_media(log=lambda line: logger.info(line))
    except Exception as e:
        print(f"Error while migrating image storage: {e}")

migrate_media_layout()

def convert_media_store():
    """Idempotent; runs on a media worker so startup is not held up."""
    try:
        from api import media
        from api.media_convert import convert_media
        media.submit(convert_media, log=lambda line: logger.info(line))
    except Exception as e:
        print(f"Error while scheduling image conversion: {e}")

convert_media_store()

serve(app, host='0.0.0.0', port=int(os.environ.get('VERTIGO_PORT') or 6166), threads=8)