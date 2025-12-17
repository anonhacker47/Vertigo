import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


def as_bool(value):
    if value:
        return value.lower() in ['true', 'yes', 'on', '1']
    return False


class Config:
    # database options
    ALCHEMICAL_DATABASE_URL = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'Config/vertigo.sqlite')
    ALCHEMICAL_ENGINE_OPTIONS = {'echo': as_bool(os.environ.get('SQL_ECHO'))}

    # security options
    SECRET_KEY = os.environ.get('SECRET_KEY', 'top-secret!')
    DISABLE_AUTH = as_bool(os.environ.get('DISABLE_AUTH'))
    ACCESS_TOKEN_MINUTES = int(os.environ.get('ACCESS_TOKEN_MINUTES') or '60')
    REFRESH_TOKEN_DAYS = int(os.environ.get('REFRESH_TOKEN_DAYS') or '7')
    REFRESH_TOKEN_IN_COOKIE = as_bool(os.environ.get(
        'REFRESH_TOKEN_IN_COOKIE') or 'YES')
    REFRESH_TOKEN_IN_BODY = as_bool(os.environ.get('REFRESH_TOKEN_IN_BODY'))
    RESET_TOKEN_MINUTES = int(os.environ.get('RESET_TOKEN_MINUTES') or '15')
    PASSWORD_RESET_URL = os.environ.get('PASSWORD_RESET_URL') or \
        'http://localhost:3000/reset'
    USE_CORS = as_bool(os.environ.get('USE_CORS') or 'yes')
    CORS_SUPPORTS_CREDENTIALS = True

    raw_origins = os.environ.get('CORS_ORIGINS', '')
    CORS_ORIGINS = [origin.strip() for origin in raw_origins.split(',') if origin.strip()]  

    PACKAGE_VERSION = os.environ.get('PACKAGE_VERSION', '0.0.1')

    # API documentation
    APIFAIRY_TITLE = 'Vertigo API'
    APIFAIRY_VERSION = '0.0.2'
    APIFAIRY_UI = os.environ.get('DOCS_UI', 'elements')