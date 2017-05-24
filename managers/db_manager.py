"""

"""
from __future__ import print_function

import datetime
import logging

from google.appengine.ext import ndb

from db_entities import Issue, Series

# create logger
logger = logging.getLogger(__name__)


class DB_manager:
    """
    Manages the database
    """

    def save_to_DB(self, item):
        """
        Saves the parsed issue into the database
        :param item: parsed issue
        """
        logger.debug("saving the issues")
        issue = Issue(id=item['title'])
        issue.title = item['title']
        if 'subtitle' in item:
            if any(word in item['subtitle'] for word in ["variant", "Variant"]):
                issue.key = ndb.Key(Issue, item['title'] + " variant")
                logger.debug("found variant, new issue id is " + item['title'] + " variant")
            issue.subtitle = item['subtitle']

        if 'series' in item:
            series = Series(id=item['series'].rstrip('1234567890 '), title=item['series'].rstrip('1234567890 '))
            series.put()
            issue.series = series.key

        if 'reprint' in item:
            issue.reprint = item['reprint']

        if 'url' in item:
            issue.url = item['url']
        else:
            issue.url = "#"

        if 'summary' in item:
            issue.summary = item['summary']

        if 'date' in item:
            issue.date = item['date']

        if 'price' in item:
            issue.price = item['price']

        if "placeholder/default/no-photo" in item['image']:
            issue.image = item['image']
        else:
            issue.image = item['image'].replace('small_image/200x', 'image')

        issue.put_async()
        logger.debug("issue " + issue.title + " saved")

    def del_all(self, items):
        """
        deletes a collection of items from the database
        :param items: items to delete
        """
        for item in items:
            item.key.delete()
        logger.debug("Deleted all the items")

    def to_json(self, o):
        """
        converts a database object to a json-compatible format
        :param o: generic object
        :return: generic object
        """
        if isinstance(o, list):
            return [self.to_json(l) for l in o]
        if isinstance(o, dict):
            x = {}
            for l in o:
                x[l] = self.to_json(o[l])
            return x
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, ndb.GeoPt):
            return {'lat': o.lat, 'lon': o.lon}
        if isinstance(o, ndb.Key):
            return o.urlsafe()
        if isinstance(o, ndb.Model):
            dct = o.to_dict()
            dct['id'] = o.key.id()
            return self.to_json(dct)
        return o
