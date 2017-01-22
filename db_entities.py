from google.appengine.ext import ndb


class Issue(ndb.Model):
    title = ndb.StringProperty(indexed=True)
    subtitle = ndb.StringProperty(indexed=False)
    serie = ndb.StringProperty(indexed=True)
    ristampa = ndb.StringProperty(indexed=False)
    data = ndb.DateProperty(indexed=True)
    prezzo = ndb.StringProperty(indexed=False)
    image = ndb.StringProperty(indexed=False)


class DBMan:
    def del_all(self, items):
        for item in items:
            item.key.delete()
