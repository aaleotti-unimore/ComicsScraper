"""Public API module.

.. module:: api
   :platform: Unix
   :synopsis: Here there are all the handlers for the public APIs 

.. moduleauthor:: Alessandro Aleotti <71196@studenti.unimore.it>


"""

from __future__ import unicode_literals

import logging

import bleach
from flask import Blueprint, make_response
from flask import jsonify
from google.appengine.ext import ndb

from models.models import Issue, Series
from models.models import Users
from query import Query
from utils import to_json

logger = logging.getLogger(__name__)

api = Blueprint('restful_api', __name__)


@api.route('/api/v1.0/series', methods=['GET'])
def get_all_series():
    """Returns a list of all the series 
    
    :returns: list of all the series titles
    
    """
    return make_response(jsonify({'response': to_json(Series.query().fetch())}), 200)


@api.route('/api/v1.0/series/<title>', methods=['GET'])
def get_serie(title):
    """Return the list of issues given a specific series title
    
    :param title: series title
    :returns: list of issues
    
    """
    title = bleach.clean(title)
    issues = Issue.query(Issue.series == ndb.Key(Series, title)).order(-Issue.date).fetch()
    if issues:
        return make_response(jsonify({'response': to_json(issues)}), 200)
    else:
        return make_response(jsonify({'error': 'Serie not found'}), 404)


@api.route('/api/v1.0/series/users/<userid>', methods=['GET'])
def get_user_series(userid):
    """Returns the series of a user given the google userid
    
    :param userid: google user id
    :returns: list of user series
    """
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
    """Returns all the issues in the database
    
    :returns: list of issues
    """
    return make_response(jsonify({'response': to_json(Issue.query().fetch())}))


@api.route('/api/v1.0/issues/<title>', methods=['GET'])
def get_single_issue(title):
    """ Returns all the informations of a issue number
    
    :param title: issue title 
    :returns: issue informations
    """
    title = bleach.clean(title)
    response = Issue.query(Issue.title == title).fetch()
    if response:
        return make_response(jsonify({'response': to_json(response)}), 200)
    else:
        return make_response(jsonify({'error': 'Issue not found'}), 404)


@api.route('/api/v1.0/issues/users/<userid>', methods=['GET'])
def get_user_issues(userid):
    """Return all the issues of a user, given his google user id
    
    :param userid: google user id
    :returns: list of user issues
    """
    userid = bleach.clean(userid)
    user = Users.get_by_id(userid)
    if user:
        q = Query()
        res = to_json(q.get_user_issues(user).fetch())
        return make_response(jsonify({'response': res}), 200)
    else:
        return make_response(jsonify({'error': 'User not found'}), 404)


@api.route('/api/v1.0/specials/<userid>', methods=['GET'])
def get_user_specials(userid):
    """Returns all the user specials given his google user id
    
    :param userid: google user id
    :returns: list of issues
    """
    userid = bleach.clean(userid)
    user = Users.get_by_id(userid)
    if user:
        q = Query()
        res = to_json(q.get_user_specials(user))
        return make_response(jsonify({'response': res}), 200)
    else:
        return make_response(jsonify({'error': 'User not found'}), 404)
