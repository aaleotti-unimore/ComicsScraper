from __future__ import unicode_literals, print_function

import json
import logging

from flask import render_template, request, Blueprint
from google.appengine.ext import ndb

from db_entities import Issue, Series
from managers.db_manager import DB_manager
from utils import date_handler

logger = logging.getLogger(__name__)

show_series_api = Blueprint('show_series_api', __name__)


@show_series_api.route('/show_series/get/', methods=['POST'])
def get_series():
    """
    Fetch the requested series
    :return: returns a JSON object containing all the issues from the series; ordered by date
    """
    series_title = request.form['series']
    logger.debug("REQUESTED SERIE:" + request.form['series'])
    dbm = DB_manager()
    if series_title:
        series_id = ndb.Key(Series, series_title)
        issues = Issue.query(Issue.series == series_id).order(-Issue.date).fetch()
        dump = dbm.to_json(issues)
        logger.debug("issues sent: " + str(len(dump)))
        return json.dumps(dump, default=date_handler)


@show_series_api.route('/show_series')
def show_series_page():
    """
    Renders the "show series" page
    """
    logger.debug("retrieving all the series... ")
    series = Series.query()
    return render_template("show_series.html", series=series)
