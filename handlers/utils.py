"""
General utilities
"""

from __future__ import unicode_literals, print_function

import datetime
import logging.config

from flask import redirect, Blueprint
from google.appengine.ext import ndb

from handlers.page_parser import Parser
from models.models import Issue, Series

logger = logging.getLogger(__name__)
utils_api = Blueprint('utils_api', __name__)


def date_handler(obj):
    """
    Formats the date from a date object
    
    :param obj: date object
    :returns: date
    """
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


@utils_api.route('/tasks/weekly_update')
def database_update():
    """
    updates the database
    
    :returns: redirects to index page
    """
    MIN_PAGE = 1
    MAX_PAGE = 10
    Parser(MIN_PAGE, MAX_PAGE)
    return redirect('/')


@utils_api.route('/restricted/clean_and_parse/')
def clear_db():
    """
    Deletes all the database entries
    
    :returns: redirects to the index page
    """
    ndb.delete_multi(
        Issue.query().fetch(keys_only=True)
    )
    ndb.delete_multi(
        Series.query().fetch(keys_only=True)
    )
    database_update()
    return redirect('/')


@utils_api.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'.format(e), 404


@utils_api.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


def to_json(o):
    """
    converts an object to a json-compatible format
    
    :param o: generic object
    :returns: jsonified generic object
    """
    if isinstance(o, list):
        return [to_json(l) for l in o]
    if isinstance(o, dict):
        x = {}
        for l in o:
            x[l] = to_json(o[l])
        return x
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    if isinstance(o, ndb.GeoPt):
        return {'lat': o.lat, 'lon': o.lon}
    if isinstance(o, ndb.Key):
        return o.urlsafe()
    if isinstance(o, ndb.Model):
        dct = o.to_dict()
        dct['id'] = o.key.id()
        return to_json(dct)
    return o