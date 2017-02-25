from google.appengine.ext import ndb
import datetime


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
    url = ndb.StringProperty(indexed=False)
    desc = ndb.StringProperty(indexed=False, repeated=True)

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

class Users(ndb.Model):
    serie_list = ndb.KeyProperty(repeated=True)

