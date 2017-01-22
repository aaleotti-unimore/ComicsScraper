"""`main` is the top level module for your Flask application."""
from marvel import Parsatore
from db_entities import DBMan
from db_entities import Issue
from google.appengine.ext import ndb
# Import the Flask Framework
from flask import Flask
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    par = Parsatore()
    dbm = DBMan()
    # par.saveToDB(par.parser())
    from datetime import date
    issues = Issue.query(ndb.AND(Issue.data > date(2017, 1, 1), Issue.data < date(2017, 1, 31))).order(-Issue.data)
    # dbm.del_all(issues)

    # response  = '<html><body>'
    # self.response.out.write(par.print_items(issues))
    # self.response.out.write('</body></html>')
    return par.print_items(issues)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
