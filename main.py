"""`main` is the top level module for your Flask application."""
from datetime import datetime, timedelta

from flask import Flask, render_template, redirect
from google.appengine.ext import ndb
from parser import parsatore
from db_manager import db_manager
from werkzeug import debug


from db_entities import Issue, Serie

app = Flask(__name__)
app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, True)


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
@app.route('/index.html')
def main():
    today = datetime.today()
    start_week = today - timedelta(today.weekday())
    end_week = start_week + timedelta(7)

    issues = Issue.query(
        ndb.AND(
            ndb.OR(
                Issue.serie == ndb.Key(Serie, 'Avengers'),
                Issue.serie == ndb.Key(Serie, 'Iron Man'),
                Issue.serie == ndb.Key(Serie, 'Devil e i Cavalieri Marvel'),
                Issue.serie == ndb.Key(Serie, 'Incredibili Inumani'),
                Issue.serie == ndb.Key(Serie, 'Marvel Crossover'),
                Issue.serie == ndb.Key(Serie, 'Marvel Miniserie')
            )
        )
    ).order(Issue.data)

    if issues.count(limit=None) == 0:
        cronjob()

    week_issues = issues.filter(ndb.AND(Issue.data >= start_week, Issue.data <= end_week))
    future_issues = issues.filter(Issue.data > end_week)

    return render_template("mainpage_contents.html", issues=week_issues, issues_count=issues.count(limit=None),
                           future_issues=future_issues, future_issues_count=future_issues.count(limit=None))


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
    par = parsatore()
    dbm = db_manager()
    dbm.save_to_DB(par.parser())
    return redirect('/')


@app.route('/restricted/cleardb')
def clear_db():
    ndb.delete_multi(
        Issue.query().fetch(keys_only=True)
    )
    return redirect('/')
