from __future__ import unicode_literals

import logging

import httplib2
from flask import Blueprint, session, url_for
from flask_login import current_user
from googleapiclient import discovery
from oauth2client.client import OAuth2Credentials
from query import Query

logger = logging.getLogger(__name__)

calendar_manager_api = Blueprint('calendar_manager_api', __name__)


@calendar_manager_api.route('/add_cal')
def add_cal():
    """Builds a GMAIL API query for shipment emails in the last 6 months.
     Returns a function call asking for the contents of those shipping emails.
     """
    # query = "shipped shipping shipment tracking after:2014/1/14"

    # messages = data["messages"]
    # messages is a list of dictionaries [{ 'id': '12345', 'threadId': '12345'}, ]
    # return request_email_body(messages)
    query = Query(current_user)
    result = query.get_issues()
    issue = result['weel_issues'][0]


    event = {
        'summary': 'Google I/O 2015',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2017-04-13T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2017-04-14T17:00:00-07:00',
            'timeZone': 'Europe/Rome',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],
        'attendees': [
            {'email': 'lpage@example.com'},
            {'email': 'sbrin@example.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    credentials = OAuth2Credentials.from_json(session['credentials'])
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = service.events().insert(calendarId='primary', body=event).execute()
    logger.debug('Event created: %s' % (event.get('htmlLink')))
    return url_for('main')