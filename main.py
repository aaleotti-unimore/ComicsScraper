from __future__ import unicode_literals

from parsatore import Parsatore

"""`main` is the top level module for your Flask application."""

from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, request, jsonify, Response
from google.appengine.ext import ndb
from google.appengine.api import users
from dbmanager import DbManager
from werkzeug import debug
from dbentities import Issue, Serie, Users
import logging.config
import json

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
    # DATETIME RANGES SETTINGS
    today = datetime.today()
    start_week = today - timedelta(today.weekday())
    end_week = start_week + timedelta(7)
    start_last_week = today - timedelta(today.weekday()) - (timedelta(7))
    # END DATETIME RANGES SETTINGS

    # QUERY
    my_user = __get_user_status__()[0]
    logger.debug("main user is: " + str(my_user))
    if my_user:
        if my_user.serie_list:
            issues = Issue.query(Issue.serie.IN(my_user.serie_list)).order(Issue.data)
        else:
            issues = None
    else:
        issues = Issue.query()

    if issues:
        logger.debug("the query retrieved: " + str(issues.count()) + " elements")
    else:
        logger.debug("no Issues in the DB")

    week_issues = None
    future_issues = None
    past_issues = None
    week_issues_count = None
    future_issues_count = None
    past_issues_count = None
    week_sum = 0
    past_sum = 0
    if issues:
        week_issues = issues.filter(ndb.AND(Issue.data >= start_week, Issue.data <= end_week))
        future_issues = issues.filter(Issue.data > end_week)
        past_issues = issues.filter(ndb.AND(Issue.data >= start_last_week, Issue.data < start_week))

        week_issues_count = issues.count(limit=None),
        future_issues_count = future_issues.count(limit=None),
        past_issues_count = past_issues.count(limit=None),

        # SUM WEEKLY PRICES

        import re
        for issue in past_issues:
            past_sum += float(re.sub(",", ".", issue.prezzo[2:]))

        for issue in week_issues:
            week_sum += float(re.sub(",", ".", issue.prezzo[2:]))

            # END SUM WEEKLY PRICES

    # END QUERY

    logger.debug("week Issues Count: " + str(week_issues_count))
    logger.debug("future Issues Count: " + str(future_issues_count))
    logger.debug("past Issues Count: " + str(past_issues_count))
    nullobj = Issue(id="cul", data=today)

    return render_template("mainpage_contents.html",
                           issues=week_issues,
                           issues_count=week_issues_count,
                           week_sum=week_sum,
                           future_issues=future_issues,
                           future_issues_count=future_issues_count,
                           past_issues=past_issues,
                           past_issues_count=past_issues_count,
                           past_sum=past_sum,
                           nullobj=nullobj
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


@app.route('/user_page')
def my_page():
    logger.debug("retrieving all the series: ")
    series = Serie.query()
    for serie in series:
        logger.debug(serie.title)
    return render_template("my_lists.html", series=series)


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


@app.route('/show_series/add_issue/', methods=['POST'])
def add_issue():
    issue = request
    logger.debug(str(issue))
    return jsonify(response="response")


@app.route('/show_series/get/', methods=['POST'])
def query_serie():
    serie_title = request.form['serie']
    dbm = DbManager()
    if serie_title:
        id_serie = ndb.Key(Serie, serie_title)
        logger.debug("REQUESTED SERIE:" + request.form['serie'])
        issues = Issue.query(Issue.serie == id_serie).order(-Issue.data).fetch()
        dump = dbm.to_json(issues)
        logger.debug("issues sent: " + str(len(dump)))
        return json.dumps(dump, default=date_handler)
    else:
        return "null"


@app.route('/show_series', methods=['GET', 'POST'])
def show_page():
    logger.debug("retrieving all the series: ")
    series = Serie.query()
    if request.method == 'POST':
        pass
    else:
        logger.debug("rendering page:")
        return render_template("show_entire_series.html", series=series)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


@app.route('/tasks/weekly_update')
def cronjob():
    logger.info("Parsing all the Issues")
    # par = Parsatore(1, 6)
    # par.parser()
    par = Parsatore(5, 8)
    par.parser()
    # par = Parsatore(9, 18)
    # par.parser()
    # par = Parsatore(19, 24)
    # par.parser()
    return redirect('/')


# @app.route('/restricted/cleardb')
# def clear_db():
#     ndb.delete_multi(
#         Issue.query().fetch(keys_only=True)
#     )
#     ndb.delete_multi(
#         Serie.query().fetch(keys_only=True)
#     )
#     ndb.delete_multi(
#         Users.query().fetch(keys_only=True)
#     )
#     return redirect('/')


@app.context_processor
def series_utility():
    def list_series(items):
        list_serie = []
        for item in items:
            list_serie.append(item.title)
        return list_serie

    def getUrlKey(title):
        return ndb.Key(Issue, title).urlsafe()

    return dict(list_series=list_series, getUrlKey=getUrlKey)


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
        logger.debug("my user is: " + str(my_user))
    else:
        logger.debug("the user is not logged in")
        login_url = users.create_login_url('/')

    return [my_user, login_url, logout_url]


@app.context_processor
def inject_user():
    logger.info("Injecting User...")
    userdata = __get_user_status__()
    logger.debug("userdata: " + str(userdata))
    logger.info("end injecting user")
    return dict(my_user=userdata[0], login_url=userdata[1], logout_url=userdata[2])
