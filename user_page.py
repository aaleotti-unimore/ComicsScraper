from __future__ import unicode_literals, print_function

import logging.config

from flask import render_template, request, Blueprint
from flask_login import current_user
from google.appengine.api import users
from google.appengine.ext import ndb

from db_entities import Serie, Users

logger = logging.getLogger(__name__)
user_page_api = Blueprint('user_page_api', __name__)


@user_page_api.route('/user_page/add_series/', methods=['POST'])
def add_user_series():
    my_user = current_user
    id_serie = ndb.Key(Serie, request.form['serie'])
    if id_serie not in my_user.serie_list:
        my_user.serie_list.append(id_serie)
        my_user.put()
        logging.debug("user id:" + str(my_user) + " serie aggiunta: " + request.form['serie'])
    return show_user_page()


@user_page_api.route('/user_page/remove_series/', methods=['POST'])
def remove_user_series():
    my_user = current_user
    id_serie = ndb.Key(Serie, request.form['serie'])
    if id_serie in my_user.serie_list:
        my_user.serie_list.remove(id_serie)
        my_user.put()
        logging.debug("user id:" + str(my_user) + " serie rimossa: " + request.form['serie'])
    return show_user_page()


@user_page_api.route('/user_page')
def show_user_page():
    logger.debug("retrieving all the series: ")
    series = Serie.query()
    return render_template("user_page.html", series=series)
