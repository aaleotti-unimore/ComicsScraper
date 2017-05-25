# config.py
import os


class Config(object):
    APP_NAME = "The Amazing Kirby"
    SECRET_KEY = os.urandom(24)
    DEBUG = True
    TESTING = False
    REDIRECT_URI = "https://localhost:8080/gCallback"
    G_SECRETS = 'static/secrets/client_secrets_dev.json'


class ProductionConfig(Config):
    REDIRECT_URI = "https://amazingkirbi.appspot.com/gCallback"
    G_SECRETS = 'static/secrets/client_secrets_prod.json'
    DEBUG = True
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
