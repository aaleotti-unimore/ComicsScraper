from __future__ import unicode_literals, print_function

import json
import logging.config

from flask import request, jsonify, Blueprint
from flask_login import current_user
from google.appengine.api import users
from google.appengine.ext import ndb
from db_manager import DbManager
from query import Query

from db_entities import Issue, Users
from utils import date_handler

logger = logging.getLogger(__name__)
user_specials_api = Blueprint('user_specials_api', __name__)


@user_specials_api.route('/', methods=['POST'])
@user_specials_api.route('/index.html', methods=['POST'])
def get_specials():
    if request.method == 'POST':
        query = Query(current_user)
        dbm = DbManager()
        return json.dumps(dbm.to_json(query.get_specials()), default=date_handler)


@user_specials_api.route('/user/add_special_issue/', methods=['POST'])
def add_special_issue():
    my_user = current_user
    issue_title = request.form['special_issue']
    id_special = ndb.Key(Issue, issue_title)
    logger.debug("received " + str(request))
    if id_special not in my_user.special_list:
        my_user.special_list.append(id_special)
        my_user.put()
        logger.debug("user id:" + str(my_user.key) + " special aggiunto: " + issue_title)
        return jsonify(content=issue_title + " aggiunto")
    else:
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " non presente")
        return jsonify(content=issue_title + " gia presente")


@user_specials_api.route('/user/remove_special_issue/', methods=['POST'])
def remove_special_issue():
    my_user = current_user
    issue_title = request.form['special_issue']
    id_special = ndb.Key(Issue, issue_title)
    logger.debug("received " + str(request))
    if id_special in my_user.special_list:
        my_user.special_list.remove(id_special)
        my_user.put()
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " rimosso ")
        return jsonify(content=issue_title + " rimosso")
    else:
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " non presente")
        return jsonify(content=issue_title + " non presente")
        # return my_page()
