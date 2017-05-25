from __future__ import unicode_literals, print_function

import logging.config

from flask import render_template, request, Blueprint
from flask_login import current_user
from google.appengine.api import users
from google.appengine.ext import ndb

from models import Series, Users

logger = logging.getLogger(__name__)
user_page_api = Blueprint('user_page_api', __name__)


@user_page_api.route('/user_page/add_series/', methods=['POST'])
def add_user_series():
    """
    Adds requested series in the user's series
    :return: renders the user page
    """
    my_user = current_user
    series_id = ndb.Key(Series, request.form['series'])
    if series_id not in my_user.series_list:
        my_user.series_list.append(series_id)
        my_user.put()
        logging.debug("user id:" + str(my_user) + " added series: " + request.form['series'])
    return show_user_page()


@user_page_api.route('/user_page/remove_series/', methods=['POST'])
def remove_user_series():
    """
    remove requested series from the user's series list
    :return: renders user page
    """
    my_user = current_user
    series_id = ndb.Key(Series, request.form['series'])
    if series_id in my_user.series_list:
        my_user.series_list.remove(series_id)
        my_user.put()
        logging.debug("user id:" + str(my_user) + " removed series: " + request.form['series'])
    return show_user_page()


@user_page_api.route('/user_page')
def show_user_page():
    """
    renders the user page 
    :return: renders the user_page template
    """
    series = Series.query()
    return render_template("user_page.html", series=series)
