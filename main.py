"""
    Main module for the app
"""

from __future__ import unicode_literals, print_function

import logging.config

from flask import Flask, render_template
from flask_login import current_user, LoginManager
from google.appengine.ext import ndb
from werkzeug import debug

from config import ProductionConfig as Config
from managers.api_manager import api
from managers.calendar_manager import calendar_manager_api
from managers.issue_manager import show_issue_api
from managers.login_manager import app as user_manager_api, Anonuser
from models import Issue, Users
from query import Query
from utils import utils_api, database_update
from views.show_series import show_series_api
from views.user_page import user_page_api
from views.user_specials import user_specials_api

#####################
####     app     ####
#####################
app = Flask(__name__)
app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, False)
app.config.from_object(Config)

app.register_blueprint(show_series_api)
app.register_blueprint(user_page_api)
app.register_blueprint(utils_api)
app.register_blueprint(user_specials_api)
app.register_blueprint(user_manager_api)
app.register_blueprint(calendar_manager_api)
app.register_blueprint(api)
app.register_blueprint(show_issue_api)
#####################
####    logger   ####
#####################
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


@app.route('/')
@app.route('/index.html')
def main():
    """
    Populates the front page with all the recent and future issues. If the user is logged in, only his issues ares shown.
    If the database is emtpy, the cronjob function populates with all the entries from the Panini Store.
    :return: renders the main page with the query results
    """
    logger.debug("current user: %s" % current_user.name)

    query = Query()
    if not query.check_if_empty():
        database_update()

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
    :param id: user id 
    :return: user database object
    """
    return Users.get_by_id(id)


####################
####    utils   ####
####################

@app.context_processor
def __series_utility__():
    """
    template utilities
    :return: functions dictionary
    """

    def list_generator(items):
        """
        Generates list from a collection of items
        :param items: items
        :return: list of items
        """
        list_ = []
        for item in items:
            list_.append(item.title)
        return list_

    def get_url_key(title):
        """
        Generate an urlsafe string from an issue title
        :param title: Issue title
        :return: urlsafe string
        """
        return ndb.Key(Issue, title).urlsafe()

    def hyphenate(title):
        """
        hypenates an Issue title
        :param title: Issue title
        :return: Hypenated issue title
        """
        if title:
            return title.replace(" ", "-")

    return dict(list_series=list_generator, get_url_key=get_url_key, hyphenate=hyphenate)
