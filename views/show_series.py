"""
This modue manages the "Show Series" view.

"""

from __future__ import unicode_literals, print_function

import json
import logging

from flask import render_template, request, Blueprint
from google.appengine.ext import ndb

from handlers.database import Database
from handlers.utils import date_handler, to_json
from models.models import Issue, Series

logger = logging.getLogger(__name__)

show_series_api = Blueprint('show_series_api', __name__)


@show_series_api.route('/show_series/get/', methods=['POST'])
def get_series():
    """
    Fetch the requested series via POST
    
    :returns: returns a JSON object containing all the issues from the series; ordered by date
    """
    series_title = request.form['series']
    logger.debug("REQUESTED SERIE:" + request.form['series'])
    dbm = Database()
    if series_title:
        series_id = ndb.Key(Series, series_title)
        issues = Issue.query(Issue.series == series_id).order(-Issue.date).fetch()
        dump = to_json(issues)
        logger.debug("issues sent: " + str(len(dump)))
        return json.dumps(dump, default=date_handler)


@show_series_api.route('/show_series/all/', methods=['POST'])
def get_all_issues():
    """
    Responds to a POST request, showing all the issues in the view
    
    :returns: json object with all the issues in the database ordered by date
    """

    if request.method == 'POST':
        dbm = Database()
        all = Issue.query().order(-Issue.date).fetch()
        dump = to_json(all)
        return json.dumps(dump, default=date_handler)


@show_series_api.route('/show_series')
def show_series_page():
    """
    Renders the "show series" page

    :returns: renders the "show_series.html" template 
    """
    logger.debug("retrieving all the series... ")
    series = Series.query()
    return render_template("show_series.html", series=series)
