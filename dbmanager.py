from __future__ import print_function

import datetime
import logging

from google.appengine.ext import ndb

from dbentities import Issue, Serie

# create logger
logger = logging.getLogger(__name__)


class DbManager:
    def save_to_DB(self, item):
        logger.info("saving the issues")
        issue = Issue(id=item['title'])
        issue.title = item['title']
        if 'subtitle' in item:
            if any(word in item['subtitle'] for word in ["variant", "Variant"]):
                issue.key = ndb.Key(Issue, item['title'] + " variant")
                logger.debug("found variant, new issue id is " + item['title'] + " variant")
            issue.subtitle = item['subtitle']

        if 'serie' in item:
            serie = Serie(id=item['serie'].rstrip('1234567890 '), title=item['serie'].rstrip('1234567890 '))
            serie.put()
            issue.serie = serie.key

        if 'ristampa' in item:
            issue.ristampa = item['ristampa']

        if 'url' in item:
            issue.url = item['url']
        else:
            issue.url = "#"

        if 'desc' in item:
            issue.desc = item['desc']

        issue.data = item['data']
        issue.prezzo = item['prezzo']

        if "placeholder/default/no-photo" in item['image']:
            issue.image = item['image']
        else:
            issue.image = item['image'].replace('small_image/200x', 'image')

        issue.put_async()
        logger.debug("issue " + issue.title + " saved")

    def del_all(self, items):
        for item in items:
            item.key.delete()
        logger.debug("Deleted all the items")

    def to_json(self, o):
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
