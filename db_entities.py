from google.appengine.ext import ndb


class Serie(ndb.Model):
    title = ndb.StringProperty(indexed=True)


class Issue(ndb.Model):
    title = ndb.StringProperty(indexed=True)
    subtitle = ndb.StringProperty(indexed=False)
    serie = ndb.KeyProperty(Serie)
    ristampa = ndb.StringProperty(indexed=False)
    data = ndb.DateProperty(indexed=True)
    prezzo = ndb.StringProperty(indexed=False)
    image = ndb.StringProperty(indexed=False)


class DBMan:
    def save_to_DB(self, items):
        series_key_list=[]
        for item in items:
            issue = Issue()
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
            issue.image = item['image'].replace('small_image/200x','image')
            issue.put()
            print "issue " + issue.title + " saved"

    def del_all(self, items):
        for item in items:
            item.key.delete()

    def get_series(self, items):
        list_serie = []
        for item in items:
            list_serie.append(item.title)
        return list_serie
