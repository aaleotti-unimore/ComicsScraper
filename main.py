from __future__ import unicode_literals, print_function

import logging.config

from flask import Flask, render_template
from flask_login import current_user, LoginManager
from google.appengine.ext import ndb
from werkzeug import debug

from config import Config
from db_entities import Issue
from db_entities import Users
from login_manager import user_manager_api, Anonuser
from query import Query
from show_series import show_series_api
from user_page import user_page_api
from user_specials import user_specials_api
from utils import utils_api, cronjob

# create the app
app = Flask(__name__)
app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, True)
app.secret_key = Config.SECRET_KEY
app.debug = True

app.register_blueprint(show_series_api)
app.register_blueprint(user_page_api)
app.register_blueprint(utils_api)
app.register_blueprint(user_specials_api)
app.register_blueprint(user_manager_api)

# logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


@app.route('/')
@app.route('/index.html')
def main():
    query = Query(current_user)

    if query.check_if_empty() is 0:
        cronjob()

    issues_result = query.get_issues()
    logger.debug("current user: %s" % current_user)
    return render_template("mainpage_contents.html",
                           issues=issues_result['week_issues'],
                           week_sum=issues_result['week_issues_sum'],
                           week_issues_count=issues_result['week_issues_count'],
                           future_issues=issues_result['future_issues'],
                           future_issues_count=issues_result['future_issues_count'],
                           past_issues=issues_result['past_issues'],
                           past_sum=issues_result['past_issues_sum'],
                           past_issues_count=issues_result['past_issues_count'],
                           nullobj=issues_result['nullobj'],
                           )


#####################
#### flask-login ####
#####################


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = Anonuser
login_manager.session_protection = "strong"


@login_manager.user_loader
def user_loader(id):
    my_user = Users.get_by_id(id)
    return my_user


####################
####    utils   ####
####################

@app.context_processor
def __series_utility__():
    def list_series(items):
        list_serie = []
        for item in items:
            list_serie.append(item.title)
        return list_serie

    def get_url_key(title):
        return ndb.Key(Issue, title).urlsafe()

    def hyphenate(title):
        if title:
            return title.replace(" ", "-")

    return dict(list_series=list_series, get_url_key=get_url_key, hyphenate=hyphenate)
