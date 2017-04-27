from logging import getLogger

import httplib2
from apiclient import errors
from flask import redirect, request, url_for, session, Blueprint
from flask_login import login_user, AnonymousUserMixin, logout_user
from googleapiclient.discovery import build
from oauth2client import client
from oauth2client.contrib.appengine import StorageByKeyName
from db_entities import Users, CredentialsModel

app = Blueprint('user_manager_api', __name__)

logger = getLogger(__name__)


class Anonuser(AnonymousUserMixin):
    name = "Anon"
    serie_list = None


@app.route('/login')
def auth_user():
    """
    User login procedure. if the credentials are not in session, the user is redirected to the Google login panel
    :return: redirects to authorization callback
    """
    if 'credentials' not in session:
        return redirect(url_for('user_manager_api.gCallback'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('user_manager_api.gCallback'))
    else:
        # session.pop('google_token', None)
        # return redirect(url_for('user_manager_api.gCallback'))
        return redirect(url_for('main'))


@app.route('/gCallback')
def gCallback():
    """
    OAuth2 authorization flow
    """
    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope=['profile', 'email', 'https://www.googleapis.com/auth/calendar'],
        redirect_uri=url_for('user_manager_api.gCallback', _external=True),
    )
    flow.params['access_type'] = 'offline'  # offline access
    flow.params['include_granted_scopes'] = 'true'  # incremental auth
    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        save_user(credentials)
        return redirect(url_for('main'))


def save_user(credentials):
    """
    Saving and logging user to the app
    :param credentials: authorization credentials 
    """
    user_data = get_user_info(credentials)
    new_user = Users.get_or_insert(user_data['id'])
    new_user.id = user_data['id']
    new_user.name = user_data['name']
    new_user.email = user_data['email']
    session['user_email'] = user_data['email']
    new_user.put()
    storage = StorageByKeyName(CredentialsModel, new_user.id, 'credentials')
    storage.put(credentials)
    login_user(new_user, remember=True)


def get_user_info(credentials):
    """Send a request to the UserInfo API to retrieve the user's information.
    :param credentials: oauth2client.client.OAuth2Credentials instance to authorize the request.
    Returns: User information as a dict.
    """
    user_info_service = build(
        serviceName='oauth2', version='v2',
        http=credentials.authorize(httplib2.Http()))
    user_info = None
    try:
        user_info = user_info_service.userinfo().get().execute()
    except errors.HttpError as e:
        logger.error('An error occurred: %s', e)
    if user_info and user_info.get('id'):
        return user_info
    else:
        raise Exception


@app.route('/logout')
def logout():
    """
    Invalidates session and logout user
    :return: redirect to main page
    """
    session.pop('google_token', None)
    session.pop('credentials', None)
    logout_user()
    return redirect(url_for('main'))
