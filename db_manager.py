from __future__ import print_function

from db_entities import Issue, Serie


class db_manager:
    def save_to_DB(self, items):
        for item in items:
            issue = Issue(id=item['title'])
            issue.title = item['title']
            if 'subtitle' in item:
                issue.subtitle = item['subtitle']
            if 'serie' in item:
                serie = Serie(id=item['serie'].strip('1234567890 '), title=item['serie'].strip('1234567890 '))
                serie.put()
                issue.serie = serie.key
            if 'ristampa' in item:
                issue.ristampa = item['ristampa']
            issue.data = item['data']
            issue.prezzo = item['prezzo']
            if "placeholder/default/no-photo" in item['image']:
                issue.image = item['image']
            else:
                issue.image = item['image'].replace('small_image/200x', 'image')
            issue.put_async()
            # print("issue " + issue.title + " saved")

    def del_all(self, items):
        for item in items:
            item.key.delete()

    def get_series(self, items):
        list_serie = []
        for item in items:
            list_serie.append(item.title)
        return list_serie
