from __future__ import unicode_literals, print_function

from page_parser import Parsatore
from flask import Flask, render_template, redirect, request, jsonify, url_for, session
from google.appengine.ext import ndb
from google.appengine.api import users
from db_manager import DbManager
from werkzeug import debug
from db_entities import Issue, Serie, Users
from query import Query
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from urllib2 import HTTPError
import logging.config
import json
from config import Auth, Config
from requests_oauthlib.oauth2_session import OAuth2Session

# from OpenSSL import SSL
# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('yourserver.key')
# context.use_certificate_file('yourserver.crt')
# create the app
app = Flask(__name__)
app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, True)
app.secret_key = Config.SECRET_KEY
# app.run(host='127.0.0.1',port='12344',
#         debug = False/True, ssl_context=context)
# login-manager
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

# logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


@app.route('/')
@app.route('/index.html')
def main():
    query = Query(users.get_current_user())
    if query.check_if_empty() is 0:
        cronjob()
    issues_result = query.get_issues()
    logger.debug("current user: %s" % (users.get_current_user()))
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


@app.route('/gCallback')
def callback():
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has
        # successfully authenticated our app.
        logger.debug("callback session['oauth_state']" + session['oauth_state'])
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            user_id = user_data['id']
            user = Users.get_or_insert(user_id)
            user.id = user_id
            logger.debug("user token: " + token)
            user.tokens = json.dumps(token)
            user.put()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    logger.debug("Google AUTH: " + str(google))
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    logger.debug("State " + str(state))
    session['oauth_state'] = state
    logger.debug("session['oauth_state'] "+ session['oauth_state'])
    return render_template('login.html', auth_url=auth_url)


@app.route('/', methods=['POST'])
@app.route('/index.html', methods=['POST'])
def get_specials():
    if request.method == 'POST':
        query = Query(__get_user_status__()[0])
        dbm = DbManager()
        dump = dbm.to_json(query.get_specials())
        return json.dumps(dump, default=date_handler)


@app.route('/user_page/add_series/', methods=['POST'])
def add_user_series():
    my_user = Users.get_by_id(users.get_current_user().user_id())
    id_serie = ndb.Key(Serie, request.form['serie'])
    if id_serie not in my_user.serie_list:
        my_user.serie_list.append(id_serie)
        my_user.put()
        logging.debug("user id:" + str(my_user) + " serie aggiunta: " + request.form['serie'])
    return show_user_page()


@app.route('/user_page/remove_series/', methods=['POST'])
def remove_user_series():
    my_user = Users.get_by_id(users.get_current_user().user_id())
    id_serie = ndb.Key(Serie, request.form['serie'])
    if id_serie in my_user.serie_list:
        my_user.serie_list.remove(id_serie)
        my_user.put()
        logging.debug("user id:" + str(my_user) + " serie rimossa: " + request.form['serie'])
    return show_user_page()


@app.route('/user/add_special_issue/', methods=['POST'])
def add_special_issue():
    my_user = Users.get_by_id(users.get_current_user().user_id())
    issue_title = request.form['special_issue']
    id_special = ndb.Key(Issue, issue_title)
    logger.debug("received " + str(request))
    if id_special not in my_user.special_list:
        my_user.special_list.append(id_special)
        my_user.put()
        logger.debug("user id:" + str(my_user.key) + " special aggiunto: " + issue_title)
        return jsonify(content=issue_title + " aggiunto")
    else:
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " non presente")
        return jsonify(content=issue_title + " gia presente")


@app.route('/user/remove_special_issue/', methods=['POST'])
def remove_special_issue():
    my_user = Users.get_by_id(users.get_current_user().user_id())
    issue_title = request.form['special_issue']
    id_special = ndb.Key(Issue, issue_title)
    logger.debug("received " + str(request))
    if id_special in my_user.special_list:
        my_user.special_list.remove(id_special)
        my_user.put()
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " rimosso ")
        return jsonify(content=issue_title + " rimosso")
    else:
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " non presente")
        return jsonify(content=issue_title + " non presente")
        # return my_page()


@app.route('/user_page')
def show_user_page():
    logger.debug("retrieving all the series: ")
    series = Serie.query()
    return render_template("user_page.html", series=series)


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


@app.route('/show_series/get/', methods=['POST'])
def get_series():
    serie_title = request.form['serie']
    logger.debug("REQUESTED SERIE:" + request.form['serie'])
    dbm = DbManager()
    if serie_title:
        id_serie = ndb.Key(Serie, serie_title)
        issues = Issue.query(Issue.serie == id_serie).order(-Issue.data).fetch()
        dump = dbm.to_json(issues)
        logger.debug("issues sent: " + str(len(dump)))
        return json.dumps(dump, default=date_handler)


@app.route('/show_series')
def show_series_page():
    logger.debug("retrieving all the series... ")
    series = Serie.query()
    return render_template("show_series.html", series=series)


@app.route('/tasks/weekly_update')
def cronjob():
    logger.info("Parsing all the Issues")
    Parsatore(1, 10)
    return redirect('/')


# @app.route('/restricted/clean_and_parse/')
def clear_db():
    ndb.delete_multi(
        Issue.query().fetch(keys_only=True)
    )
    ndb.delete_multi(
        Serie.query().fetch(keys_only=True)
    )
    cronjob()
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'.format(e), 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


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


def __get_user_status__(my_user_id):
    logger.debug("Getting user status")
    if my_user_id:
        my_user_id = Users.get_or_insert(my_user_id)
        my_user_id.put()
        logger.debug("the user is logged in/registerd")
        logger.debug("my user is: " + str(my_user_id.key.id()))
    else:
        logger.debug("the user is not logged in")

    return my_user_id


@login_manager.user_loader
def load_user(id):
    return Users.get_by_id(id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
