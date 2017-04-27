from __future__ import unicode_literals, print_function

import json
import logging.config

from flask import request, jsonify, Blueprint
from flask_login import current_user
from google.appengine.ext import ndb

from db_entities import Issue
from managers.db_manager import db_manager
from query import Query
from utils import date_handler

logger = logging.getLogger(__name__)
user_specials_api = Blueprint('user_specials_api', __name__)


@user_specials_api.route('/', methods=['POST'])
@user_specials_api.route('/index.html', methods=['POST'])
def get_specials():
    """
    Retrieves user's special issues.
    :return: JSON object with user's special issues
    """
    if request.method == 'POST':
        query = Query()
        dbm = db_manager()
        return json.dumps(dbm.to_json(query.get_specials()), default=date_handler)


@user_specials_api.route('/user/add_special_issue/', methods=['POST'])
def add_special_issue():
    """
    Adds requested issue to the user's specials list
    :return: 
    """
    my_user = current_user
    issue_title = request.form['special_issue']
    special_id = ndb.Key(Issue, issue_title)
    logger.debug("received " + str(request))
    if special_id not in my_user.specials_list:
        my_user.specials_list.append(special_id)
        my_user.put()
        logger.debug("user id:" + str(my_user.key) + " special added: " + issue_title)
        return jsonify(content=issue_title + " added")
    else:
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " non found")
        return jsonify(content=issue_title + " already added")


@user_specials_api.route('/user/remove_special_issue/', methods=['POST'])
def remove_special_issue():
    """
    Removes requested issue from the user's specials list
    :return: 
    """
    my_user = current_user
    issue_title = request.form['special_issue']
    special_id = ndb.Key(Issue, issue_title)
    logger.debug("received " + str(request))
    if special_id in my_user.specials_list:
        my_user.specials_list.remove(special_id)
        my_user.put()
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " removed ")
        return jsonify(content=issue_title + " removed")
    else:
        logger.debug("user id:" + str(my_user.key) + " special " + issue_title + " not found")
        return jsonify(content=issue_title + " not found")
