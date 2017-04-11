from __future__ import unicode_literals, print_function

import json
import logging

from flask import render_template, request, Blueprint
from google.appengine.ext import ndb

from db_entities import Issue, Serie
from db_manager import DbManager
from utils import date_handler

logger = logging.getLogger(__name__)

show_series_api = Blueprint('show_series_api', __name__)
@show_series_api.route('/show_series/get/', methods=['POST'])
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


@show_series_api.route('/show_series')
def show_series_page():
    logger.debug("retrieving all the series... ")
    series = Serie.query()
    return render_template("show_series.html", series=series)


