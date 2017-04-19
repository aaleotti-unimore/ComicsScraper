"""
    Modulo principale dell'app. inizializza la flask app, il login manager e crea la pagina index
    In coda sono presenti alcuni context processor aggiuntivi per le pagine html.
"""

from __future__ import unicode_literals, print_function

import logging.config

from flask import Flask, render_template
from flask_login import current_user, LoginManager
from google.appengine.ext import ndb
from werkzeug import debug

from db_entities import Issue, Users
from login_manager import app as user_manager_api, Anonuser
from query import Query
from show_series import show_series_api
from user_page import user_page_api
from user_specials import user_specials_api
from utils import utils_api, cronjob
from config import DevelopmentConfig as Config
from calendar_manager import calendar_manager_api
import calendar_manager

#####################
####     app     ####
#####################
app = Flask(__name__)
app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, True)
app.config.from_object(Config)

app.register_blueprint(show_series_api)
app.register_blueprint(user_page_api)
app.register_blueprint(utils_api)
app.register_blueprint(user_specials_api)
app.register_blueprint(user_manager_api)
app.register_blueprint(calendar_manager_api)

#####################
####    logger   ####
#####################
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


@app.route('/')
@app.route('/index.html')
def main():
    """
    Crea un oggetto query, che si occupera' di interrgare il db con le liste di fumetti utente per poi passarle al
    template render. Se nessun utente e' loggato passera' tutte le uscite da oggi in poi.
    :return: genera la pagina index contenente i fumetti seguiti dall'utente. 
    """

    logger.debug("current user: %s" % current_user)

    query = Query(current_user)
    if not query.check_if_empty():
        cronjob()  # popola il db se e' vuoto

    issues_result = query.get_issues()
    return render_template("mainpage_contents.html", **issues_result)


#####################
#### flask-login ####
#####################


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = Anonuser
login_manager.session_protection = "strong"


@login_manager.user_loader
def user_loader(id):
    """
    helper per il modulo flask_login, ottiene un oggetto utente dal suo id.
    :param id: id utente
    :return: oggetto utente
    """
    return Users.get_by_id(id)


####################
####    utils   ####
####################

@app.context_processor
def __series_utility__():
    """
    utilities per il template 
    :return: dizionario di funzioni
    """

    def list_generator(items):
        list_ = []
        for item in items:
            list_.append(item.title)
        return list_

    def get_url_key(title):
        return ndb.Key(Issue, title).urlsafe()

    def hyphenate(title):
        if title:
            return title.replace(" ", "-")

    return dict(list_series=list_generator, get_url_key=get_url_key, hyphenate=hyphenate)
