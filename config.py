"""Flask configuration."""
import os
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
print(basedir)

class Config:
    """Base config."""
    SECRET_KEY = os.environ('SECRET_KEY')
    SESSION_COOKIE_NAME = os.environ('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.environ('PROD_DATABASE_URI')


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    use_reloader = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///stocklists.db'