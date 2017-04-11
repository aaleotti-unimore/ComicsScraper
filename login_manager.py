"""

"""
from __future__ import unicode_literals

from flask import Flask, redirect, request, url_for, session, Blueprint, g, jsonify
from flask_login import login_user, logout_user, AnonymousUserMixin
from flask_oauthlib.client import OAuth

from config import DevelopmentConfig as Config
from db_entities import Users

user_manager_api = Blueprint('user_manager_api', __name__)

app = Flask(__name__)
with app.app_context():
    oauth = OAuth(app)
    google = oauth.remote_app(
        'google',
        consumer_key=Config.CLIENT_ID,
        consumer_secret=Config.CLIENT_SECRET,
        request_token_params={
            'scope': 'email',
            'access_type': 'offline'
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )


@user_manager_api.route('/login')
def login():
    """
    
    :return: 
    """
    return google.authorize(callback=url_for(
        'user_manager_api.authorized',
        _external=True)
    )


@user_manager_api.route('/logout')
def logout():
    """
    
    :return: 
    """
    session.pop('google_token', None)
    logout_user()
    return redirect(url_for('main'))


@user_manager_api.route('/gCallback')
def authorized():
    """
    
    :return: 
    """
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    new_user = Users.get_or_insert(me.data['id'])
    new_user.id = me.data['id']
    new_user.name = me.data['name']
    new_user.put()
    login_user(new_user, remember=True)
    g.user = new_user
    return redirect(url_for('main'))
    # return jsonify({"data": me.data})


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


class Anonuser(AnonymousUserMixin):
    serie_list = None
