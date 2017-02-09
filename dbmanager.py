from __future__ import print_function

from dbentities import Issue, Serie
import logging

# create logger
logger = logging.getLogger(__name__)


class DbManager:
    def save_to_DB(self, items):
        logger.info("saving the issues")
        for item in items:
            issue = Issue(id=item['title'])
            issue.title = item['title']
            if 'subtitle' in item:
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
