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

class UserSeries(ndb.Model):
    user_id = ndb.GenericProperty(indexed=True)
    serie_list = ndb.KeyProperty(repeated=True)

