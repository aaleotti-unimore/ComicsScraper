from __future__ import unicode_literals

from page_parser import Parsatore

"""`main` is the top level module for your Flask application."""

from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, request, jsonify, Response
from google.appengine.ext import ndb
from google.appengine.api import users
from db_manager import DbManager
from werkzeug import debug
from db_entities import Issue, Serie, Users
from query import Query
import logging.config
import json
import re

logging.config.fileConfig('logging.conf')
# create logger
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, True)


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
@app.route('/index.html')
def main():
    query = Query(__get_user_status__()[0])
    issues_result = query.get_issues()
    special_result = query.get_specials()
    return render_template("mainpage_contents.html",
                           issues=issues_result['week_issues'],
                           week_sum=issues_result['week_issues_sum'],
                           future_issues=issues_result['future_issues'],
                           past_issues=issues_result['past_issues'],
                           past_sum=issues_result['past_issues_sum'],
                           nullobj=issues_result['nullobj'],
                           special_issues=special_result['special_issues'],
                           special_issues_sum=special_result['special_issues_sum']
                           )


@app.route('/user_page/add_series/', methods=['POST'])
def add_user_series():
    my_user = Users.get_by_id(users.get_current_user().user_id())
    id_serie = ndb.Key(Serie, request.form['serie'])
    if id_serie not in my_user.serie_list:
        my_user.serie_list.append(id_serie)
        logging.debug("user id:" + str(my_user) + " serie aggiunta: " + request.form['serie'])
    return my_page()


@app.route('/user_page/remove_series/', methods=['POST'])
def remove_user_series():
    my_user = Users.get_by_id(users.get_current_user().user_id())
    id_serie = ndb.Key(Serie, request.form['serie'])
    if id_serie in my_user.serie_list:
        my_user.serie_list.remove(id_serie)
        logging.debug("user id:" + str(my_user) + " serie rimossa: " + request.form['serie'])
    return my_page()


@app.route('/user/add_special_issue/', methods=['POST'])
def add_special_issue():
    my_user = Users.get_by_id(users.get_current_user().user_id())
    id_special = ndb.Key(Issue, request.form['special_issue'])
    logger.debug("received " + str(request))
    if id_special not in my_user.special_list:
        my_user.special_list.append(id_special)
        logger.debug("user id:" + str(my_user.key) + " special aggiunto: " + request.form['special_issue'])
    return my_page()


@app.route('/user/remove_special_issue/', methods=['POST'])
def remove_special_issue():
    my_user = Users.get_by_id(users.get_current_user().user_id())
    issue_title = request.form['special_issue']
    id_special = ndb.Key(Issue, issue_title)
    logger.debug("received " + str(request))
    if id_special in my_user.special_list:
        my_user.special_list.remove(id_special)
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " rimosso ")
        return jsonify(content=issue_title + " rimosso")
    else:
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " non presente")
        return jsonify(content=issue_title + " non presente")
    # return my_page()


@app.route('/user_page')
def my_page():
    logger.debug("retrieving all the series: ")
    series = Serie.query()
    return render_template("my_lists.html", series=series)


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


# @app.route('/show_series/add_issue/', methods=['POST'])
# def add_issue():
#     issue = request
#     logger.debug(str(issue))
#     return jsonify(response="response")


@app.route('/show_series/get/', methods=['POST'])
def query_serie():
    serie_title = request.form['serie']
    logger.debug("REQUESTED SERIE:" + request.form['serie'])
    dbm = DbManager()
    if serie_title:
        id_serie = ndb.Key(Serie, serie_title)
        issues = Issue.query(Issue.serie == id_serie).order(-Issue.data).fetch()
        dump = dbm.to_json(issues)
        logger.debug("issues sent: " + str(len(dump)))
        return json.dumps(dump, default=date_handler)


@app.route('/show_series', methods=['GET', 'POST'])
def show_page():
    logger.debug("retrieving all the series... ")
    series = Serie.query()
    if request.method == 'POST':
        pass
    else:
        logger.debug("rendering page...")
        return render_template("show_entire_series.html", series=series)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'.format(e), 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


@app.route('/tasks/weekly_update')
def cronjob():
    logger.info("Parsing all the Issues")
    Parsatore(2, 8)
    return redirect('/')


# @app.route('/restricted/clean_and_parse/')
# def clear_db():
#     ndb.delete_multi(
#         Issue.query().fetch(keys_only=True)
#     )
#     ndb.delete_multi(
#         Serie.query().fetch(keys_only=True)
#     )
#     cronjob()
#     return redirect('/')


@app.context_processor
def series_utility():
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


def __get_user_status__():
    my_user = None
    logout_url = None
    login_url = None
    logger.debug("Getting user status")
    google_user = users.get_current_user()
    if google_user:
        logout_url = users.create_logout_url('/')
        my_user = Users.get_or_insert(str(google_user.user_id()))
        my_user.put()
        logger.debug("the user is logged in")
        logger.debug("my user is: " + str(my_user.key.id()))
    else:
        logger.debug("the user is not logged in")
        login_url = users.create_login_url('/')

    return [my_user, login_url, logout_url]


@app.context_processor
def inject_user():
    userdata = __get_user_status__()
    logger.info("Successfully retrieved my user")
    return dict(my_user=userdata[0], login_url=userdata[1], logout_url=userdata[2])
