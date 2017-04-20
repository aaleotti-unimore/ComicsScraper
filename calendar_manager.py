from __future__ import unicode_literals

import logging

import httplib2
from flask import jsonify
from flask import url_for, Blueprint, redirect
from flask_login import current_user
from googleapiclient import discovery
from oauth2client.contrib.appengine import StorageByKeyName
from datetime import timedelta
from db_entities import Users, CredentialsModel
from query import Query

logger = logging.getLogger(__name__)

calendar_manager_api = Blueprint('calendar_manager_api', __name__)

CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
REFRESH_TOKEN = "refresh_token"

user = Users.query().fetch(limit=1)
storage = StorageByKeyName(CredentialsModel, user[0].id, 'credentials')
credentials = storage.get()
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(45)


def cal_list():
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        # for calendar_list_entry in calendar_list['items']:
        #     logger.debug(calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return calendar_list


@calendar_manager_api.route('/cal_list')
def show_list():
    calendar_list = cal_list()
    return jsonify(calendar_list)


def get_or_insert_cal():
    calendar_list = cal_list()
    for calendar in calendar_list['items']:
        if calendar['summary'] in 'Uscite Fumetti':
            return calendar['id']

    calendar = {
        'accessRole': 'reader',
        'summary': 'Uscite Fumetti',
        'timeZone': 'Europe/Rome'
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']


@calendar_manager_api.route('/del_cal')
def delete_cal():
    calendar_list = cal_list()
    ids = []
    for calendar in calendar_list['items']:
        if calendar['summary'] in 'Uscite Fumetti':
            ids.append(calendar['id'])
            logger.debug(calendar['id'])

    for id in ids:
        service.calendars().delete(calendarId=id).execute()
    return redirect(url_for('main'))


def add_issue(calendarID, issue):
    start = issue.data
    end = issue.data + timedelta(days=1)
    event = {
        'summary': issue.title,
        'start': {
            'date': start.isoformat(),
            'timeZone': 'Europe/Rome',
        },
        'end': {
            'date': end.isoformat(),
            'timeZone': 'Europe/Rome',
        },
    }

    event = service.events().insert(calendarId=calendarID, body=event).execute()
    logger.debug('Event created: %s' % (event.get('htmlLink')))
    return event

@calendar_manager_api.route('/populate/')
def populate_calendar():
    cal_id = get_or_insert_cal()
    from query import Query
    query = Query(user)
    for issue in query.get_user_issues(user[0]):
        add_issue(cal_id, issue)
    for issue in query.get_user_specials(user[0]):
        add_issue(cal_id, issue)
    return redirect(url_for('main'))