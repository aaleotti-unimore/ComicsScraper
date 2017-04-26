from __future__ import unicode_literals

import logging
import threading
from datetime import timedelta

import httplib2
from google.appengine.ext import ndb
from db_entities import Issue, Serie
from flask import jsonify
from flask import url_for, Blueprint, redirect, make_response
from google.appengine.api import urlfetch
from googleapiclient import discovery
from oauth2client.contrib.appengine import StorageByKeyName

from db_entities import Users, CredentialsModel
from query import Query
from utils import to_json

logger = logging.getLogger(__name__)

api = Blueprint('restful_api', __name__)


@api.route('/api/v1.0/issues', methods=['GET'])
def get_issues():
    return jsonify({'response': to_json(Issue.query().fetch())})

@api.route('/api/v1.0/series', methods=['GET'])
def get_series():
    return jsonify({'response': to_json(Serie.query().fetch())})


@api.route('/api/v1.0/issues/<userid>', methods=['GET'])
def get_user_issues(userid):
    user = Users.get_by_id(userid)
    if user:
        q = Query()
        res = to_json(q.get_user_issues(user).fetch())
        return jsonify({'response': res})
    else:
        return make_response(jsonify({'error':'not found'}), 404)


@api.route('/api/v1.0/specials/<userid>', methods=['GET'])
def get_user_specials(userid):
    user = Users.get_by_id(userid)
    if user:
        q = Query()
        res = to_json(q.get_user_specials(user))
        return jsonify({'response': res})
    else:
        return make_response(jsonify({'error':'not found'}), 404)
