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


def get_list():
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
def cal_list():
    calendar_list = get_list()
    return jsonify(calendar_list)


@calendar_manager_api.route('/create_cal')
def create_cal():
    calendar = {
        'accessRole': 'reader',
        'summary': 'Uscite Fumetti',
        'timeZone': 'Europe/Rome'
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return jsonify(created_calendar)


@calendar_manager_api.route('/del_cal')
def delete_cal():
    calendar_list = get_list()
    ids = []
    for calendar in calendar_list['items']:
        if calendar['summary'] in 'Uscite Fumetti':
            ids.append(calendar['id'])
            logger.debug(calendar['id'])

    for id in ids:
        print id
        service.calendars().delete(calendarId=id).execute()

    return redirect(url_for('main'))


@calendar_manager_api.route('/add_event')
def add_issue():
    from db_entities import Issue
    import json
    from utils import date_handler
    from datetime import datetime
    import datetime
    issue = Issue.query().fetch(limit=1)[0]
    # start = datetime.datetime.combine(issue.data, datetime.time())
    # end = datetime.datetime.combine(issue.data+timedelta(days=1), datetime.time())
    start = issue.data
    end = issue.data+timedelta(days=1)
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

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    return redirect(url_for('main'))


def to_json(o):
    import datetime
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
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    return o
