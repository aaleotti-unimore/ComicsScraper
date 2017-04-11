from __future__ import unicode_literals, print_function

import logging.config

from flask import redirect, Blueprint
from google.appengine.ext import ndb

from db_entities import Issue, Serie
from page_parser import Parsatore

logger = logging.getLogger(__name__)
utils_api = Blueprint('utils_api', __name__)


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


@utils_api.route('/tasks/weekly_update')
def cronjob():
    logger.info("Parsing all the Issues")
    Parsatore(1, 10)
    return redirect('/')


@utils_api.route('/restricted/clean_and_parse/')
def clear_db():
    ndb.delete_multi(
        Issue.query().fetch(keys_only=True)
    )
    ndb.delete_multi(
        Serie.query().fetch(keys_only=True)
    )
    cronjob()
    return redirect('/')


@utils_api.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'.format(e), 404


@utils_api.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


