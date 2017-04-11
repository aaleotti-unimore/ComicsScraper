# config.py
import json

with open('client_secret.json') as data_file:
    data = json.load(data_file)


class Auth:
    CLIENT_ID = data['web']['client_id']
    CLIENT_SECRET = data['web']['client_secret']
    REDIRECT_URI = "http://localhost:8080/gCallback"


class Config:
    APP_NAME = "The Amazing Kirby"
    SECRET_KEY = 'if you no longer go for a gap that exists, you are no longer a racing driver'
