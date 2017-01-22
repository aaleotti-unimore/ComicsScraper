"""`main` is the top level module for your Flask application."""
from datetime import datetime, timedelta

from flask import Flask
from google.appengine.ext import ndb

from CalendarGenerator import CalendarGenerator
from db_entities import DBMan
from db_entities import Issue, Serie
from marvel import Parsatore

app = Flask(__name__)


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    par = Parsatore()
    dbm = DBMan()
    cal = CalendarGenerator()

    # dbm.del_all(Issue.query())
    # dbm.del_all(Serie.query())
    if Issue.query().count(limit=None) == 0:
        dbm.save_to_DB(par.parser())
    series = dbm.get_series(Serie.query())
    str = ""
    for serie in series:
        str += "<br>" + serie

    today = datetime.today()
    issues = Issue.query(
        ndb.AND(
            ndb.OR(Issue.serie == ndb.Key(Serie, 'Avengers'),
                   Issue.serie == ndb.Key(Serie, 'Iron Man'),
                   Issue.serie == ndb.Key(Serie, 'Devil e i Cavalieri Marvel'),
                   Issue.serie == ndb.Key(Serie, 'Incredibili Inumani'),
                   Issue.serie == ndb.Key(Serie, 'Marvel Crossover'),
                   Issue.serie == ndb.Key(Serie, 'Marvel Miniserie')
                   ),
            Issue.data >= today - timedelta(days=20))).order(Issue.data)
    return par.print_items(issues)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
