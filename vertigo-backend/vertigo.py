from waitress import serve
from run import app

import logging
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

serve(app, host='0.0.0.0', port=6166)