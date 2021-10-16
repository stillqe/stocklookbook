"""Flask configuration."""
from os import environ, path




class Config:
    """Base config."""

    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False

    database_uri = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}?sslmode=require'.format(
        dbuser=environ.get('DBUSER'),
        dbpass=environ.get('DBPASS'),
        dbhost=environ.get('DBHOST'),
        dbname=environ.get('DBNAME')
    )
    SQLALCHEMY_DATABASE_URI = database_uri
    SECRET_KEY = environ.get('SECRET_KEY')
    SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')


class DevConfig(Config):
    from dotenv import load_dotenv
    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, '.env'))

    FLASK_ENV = 'development'
    DEBUG = True
    use_reloader = False
    TESTING = True

    database_uri = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}?sslmode=require'.format(
        dbuser=environ.get('DBUSER'),
        dbpass=environ.get('DBPASS'),
        dbhost=environ.get('DBHOST'),
        dbname=environ.get('DBNAME')
    )
    SQLALCHEMY_DATABASE_URI = database_uri
    SECRET_KEY = environ.get('SECRET_KEY')
    SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')

class TestConfig:
    SECRET_KEY = '0AK8GsHF7tCdDBz9tJHRkQ'
    SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_DATABASE_URI = 'postgresql://stillqe:3NICEtown!@stocklookbookdb.postgres.database.azure.com/postgres?sslmode=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False