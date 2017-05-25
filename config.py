# config.py
import os


class Config(object):
    APP_NAME = "The Amazing Kirby"
    SECRET_KEY = os.urandom(24)
    DEBUG = True
    TESTING = False
    REDIRECT_URI = "https://localhost:8080/gCallback"


class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'
    REDIRECT_URI = "https://amazingkirbi.appspot.com/gCallback"
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
