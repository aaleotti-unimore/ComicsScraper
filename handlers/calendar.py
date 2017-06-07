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

from models.models import Users, CredentialsModel
from query import Query

logger = logging.getLogger(__name__)

calendar_manager_api = Blueprint('calendar_manager_api', __name__)

urlfetch.set_default_fetch_deadline(45)


def cal_list(service):
    """
    List user's calendar
    
    :param service: service
    :returns: list of calendars
    """
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return calendar_list


@calendar_manager_api.route('/cal_list/<userid>')
def show_list(userid):
    """
    Returns a JSON object with user's calendars
    
    :param userid: user id
    :returns: JSON calendar list
    """
    service = create_service(userid)
    calendar_list = cal_list(service)
    return jsonify(calendar_list)


@calendar_manager_api.route('/del_cal/<userid>')
def delete_cal(userid):
    """
    Delete the comics calendar
    
    :param userid: user id
    :returns: redirects to main page
    """
    service = create_service(userid)
    calendar_list = cal_list(service)
    for calendar in calendar_list['items']:
        if calendar['summary'] in 'Uscite Fumetti':
            service.calendars().delete(calendarId=calendar['id']).execute()

    return redirect(url_for('main'))


def get_or_insert_cal(service):
    """
    Gets the Comics calendar. if the calendar is not found, a new calendar will be created
    
    :param service: service
    :returns: comics calendar id
    """
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
    """
    Adds an issue the comics calendar
    
    :param service: service
    :param calendarID: comics calendar id
    :param issue: issue
    :returns: calendar event object
    """
    start = issue.date
    end = issue.date + timedelta(days=1)
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
        'description': '\n'.join(issue.summary),
        'locked': True
    }
    event = service.events().insert(calendarId=calendarID, body=event).execute()
    logger.debug('Event created: %s' % (event.get('htmlLink')))
    return event


@calendar_manager_api.route('/populate/<userid>')
def populate_user_calendar(userid):
    """
    Populates user's comics calendar
    
    :param userid: user id
    :returns: renders main page
    """
    user = Users.get_by_id(userid)
    logger.debug("populating user " + user.name + " calendar")
    service = create_service(userid)
    cal_id = get_or_insert_cal(service)
    clear_calendar(service, cal_id)
    query = Query()
    user_issues = query.get_user_issues(user)
    from pprint import pprint
    pprint(user_issues)
    if user_issues:
        for issue in user_issues:
            add_issue(service, cal_id, issue)
    user_specials= query.get_user_specials(user)
    if user_specials:
        for issue in user_specials:
            add_issue(service, cal_id, issue)
    return redirect(url_for('main'))


@calendar_manager_api.route('/populate_users_calendar/')
def populate_all_calendars():
    """
    CRON JOB
    Concurrently populates all users' calendars 
    
    :returns: renders main page when finished
    """
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
    """
    Clears a calendar from all the events
    
    :param service: service
    :param cal_id: calendar id
    """
    page_token = None
    while True:
        events = service.events().list(calendarId=cal_id, pageToken=page_token).execute()
        for event in events['items']:
            service.events().delete(calendarId=cal_id, eventId=event['id']).execute()
        page_token = events.get('nextPageToken')
        if not page_token:
            break


def create_service(userid):
    """
    Google Calendar API service creation
    
    :param userid: user id 
    :returns: service
    """
    storage = StorageByKeyName(CredentialsModel, userid, 'credentials')
    credentials = storage.get()
    http = credentials.authorize(httplib2.Http())
    urlfetch.set_default_fetch_deadline(45)
    return discovery.build('calendar', 'v3', http=http)
