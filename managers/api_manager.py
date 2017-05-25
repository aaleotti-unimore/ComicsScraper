from __future__ import unicode_literals

import logging
from datetime import datetime

import bleach
from flask import Blueprint, make_response
from flask import jsonify
from google.appengine.ext import ndb

from models import Issue, Series
from models import Users
from query import Query

logger = logging.getLogger(__name__)

api = Blueprint('restful_api', __name__)


@api.route('/api/v1.0/series', methods=['GET'])
def get_all_series():
    return make_response(jsonify({'response': to_json(Series.query().fetch())}))


@api.route('/api/v1.0/series/<title>', methods=['GET'])
def get_serie(title):
    title = bleach.clean(title)
    issues = Issue.query(Issue.series == ndb.Key(Series, title)).order(-Issue.date).fetch()
    if issues:
        return make_response(jsonify({'response': to_json(issues)}), 200)
    else:
        return make_response(jsonify({'error': 'serie not found'}), 404)


@api.route('/api/v1.0/series/users/<userid>', methods=['GET'])
def get_user_series(userid):
    userid = bleach.clean(userid)
    user = Users.get_by_id(userid)
    if user:
        res = {}
        for idx, serie in enumerate(user.serie_list):
            res[idx] = serie.get().title
        res = to_json(res)
        return make_response(jsonify({'response': res}), 200)
    else:
        return make_response(jsonify({'error': 'user not found'}), 404)


@api.route('/api/v1.0/issues', methods=['GET'])
def get_issues():
    return make_response(jsonify({'response': to_json(Issue.query().fetch())}))


@api.route('/api/v1.0/issues/<title>', methods=['GET'])
def get_single_issue(title):
    title = bleach.clean(title)
    return make_response(jsonify({'response': to_json(Issue.query(Issue.title == title).fetch())}))


@api.route('/api/v1.0/issues/users/<userid>', methods=['GET'])
def get_user_issues(userid):
    userid = bleach.clean(userid)
    user = Users.get_by_id(userid)
    if user:
        q = Query()
        res = to_json(q.get_user_issues(user).fetch())
        return make_response(jsonify({'response': res}), 200)
    else:
        return make_response(jsonify({'error': 'user not found'}), 404)


@api.route('/api/v1.0/specials/<userid>', methods=['GET'])
def get_user_specials(userid):
    userid = bleach.clean(userid)
    user = Users.get_by_id(userid)
    if user:
        q = Query()
        res = to_json(q.get_user_specials(user))
        return make_response(jsonify({'response': res}), 200)
    else:
        return make_response(jsonify({'error': 'user not found'}), 404)


def to_json(o):
    """

    :param o: 
    :return: 
    """
    if isinstance(o, list):
        return [to_json(l) for l in o]
    if isinstance(o, dict):
        x = {}
        for l in o:
            x[l] = to_json(o[l])
        return x
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, ndb.GeoPt):
        return {'lat': o.lat, 'lon': o.lon}
    if isinstance(o, ndb.Key):
        return o.get().title
    if isinstance(o, ndb.Model):
        dct = o.to_dict()
        dct['id'] = o.key.id()
        return to_json(dct)
    return o
