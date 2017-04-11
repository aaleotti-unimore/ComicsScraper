# config.py
import os


class Config(object):
    APP_NAME = "The Amazing Kirby"
    SECRET_KEY = os.urandom(24)
    DEBUG = False
    TESTING = False
    REDIRECT_URI = "https://localhost:8080/gCallback"
    CLIENT_ID = '830180249780-kq1046ma4m11ot3n3nps1kvbqf3o32nf.apps.googleusercontent.com'
    CLIENT_SECRET = 'M9KAAc-mStwqoi3c-zZ6HZfS'


class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'
    REDIRECT_URI = "https://amazingkirbi.appspot.com/gCallback"
    CLIENT_ID = '830180249780-80if435ls7mht053f65voa5cl5kt62ff.apps.googleusercontent.com'
    CLIENT_SECRET = 'THd1PqBmmQesZq8sqIcTz3uv'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
