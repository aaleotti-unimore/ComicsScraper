from __future__ import unicode_literals

import logging
import threading
from datetime import timedelta

import httplib2
from flask import jsonify
from flask import url_for, Blueprint, redirect
from google.appengine.api import urlfetch
from googleapiclient import discovery
from oauth2client.contrib.appengine import StorageByKeyName

from db_entities import Users, CredentialsModel
from query import Query

logger = logging.getLogger(__name__)

calendar_manager_api = Blueprint('calendar_manager_api', __name__)

urlfetch.set_default_fetch_deadline(45)


def cal_list(service):
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return calendar_list


@calendar_manager_api.route('/cal_list/<userid>')
def show_list(userid):
    service = create_service(userid)
    calendar_list = cal_list(service)
    return jsonify(calendar_list)


@calendar_manager_api.route('/del_cal/<userid>')
def delete_cal(userid):
    service = create_service(userid)
    calendar_list = cal_list(service)
    for calendar in calendar_list['items']:
        if calendar['summary'] in 'Uscite Fumetti':
            service.calendars().delete(calendarId=calendar['id']).execute()

    return redirect(url_for('main'))


def get_or_insert_cal(service):
    calendar_list = cal_list(service)
    for calendar in calendar_list['items']:
        if calendar['summary'] in 'Uscite Fumetti':
            return calendar['id']

    calendar = {
        'summary': 'Uscite Fumetti',
        'timeZone': 'Europe/Rome',
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']


def add_issue(service, calendarID, issue):
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
        'source': {
            'url': issue.url,
            'title': issue.title
        },
        'description': '\n'.join(issue.desc),
        'locked': True
    }
    event = service.events().insert(calendarId=calendarID, body=event).execute()
    logger.debug('Event created: %s' % (event.get('htmlLink')))
    return event


@calendar_manager_api.route('/populate/<userid>')
def populate_user_calendar(userid):
    user = Users.get_by_id(userid)
    logger.debug("populating user " + user.name + " calendar")
    service = create_service(userid)
    cal_id = get_or_insert_cal(service)
    clear_calendar(service, cal_id)
    query = Query()
    for issue in query.get_user_issues(user):
        add_issue(service, cal_id, issue)
    for issue in query.get_user_specials(user):
        add_issue(service, cal_id, issue)
    return redirect(url_for('main'))


@calendar_manager_api.route('/populate_users_calendar/')
def populate_all_calendars():
    users = Users.query().fetch()
    threads = [threading.Thread(target=populate_user_calendar, args=(user.id,)) for user in users]
    for t in threads:
        logger.debug("start populating thread " + t.name)
        t.start()
    for t in threads:
        logger.debug("end populating thread " + t.name)
        t.join()
    return redirect(url_for('main'))


def clear_calendar(service, cal_id):
    page_token = None
    while True:
        events = service.events().list(calendarId=cal_id, pageToken=page_token).execute()
        for event in events['items']:
            service.events().delete(calendarId=cal_id, eventId=event['id']).execute()
        page_token = events.get('nextPageToken')
        if not page_token:
            break


def create_service(userid):
    storage = StorageByKeyName(CredentialsModel, userid, 'credentials')
    credentials = storage.get()
    http = credentials.authorize(httplib2.Http())
    urlfetch.set_default_fetch_deadline(45)
    return discovery.build('calendar', 'v3', http=http)
