from flask_login import UserMixin
from google.appengine.ext import ndb

from oauth2client.contrib.appengine import CredentialsNDBProperty


class CredentialsModel(ndb.Model):
    credentials = CredentialsNDBProperty()


class Serie(ndb.Model):
    """
    Modello per una serie di fumetti
    """
    title = ndb.StringProperty(indexed=True)


class Issue(ndb.Model):
    """
    Modello di un numero
    """
    title = ndb.StringProperty(indexed=True)
    subtitle = ndb.StringProperty(indexed=False)
    serie = ndb.KeyProperty(Serie)
    ristampa = ndb.StringProperty(indexed=False)
    data = ndb.DateProperty(indexed=True)
    prezzo = ndb.StringProperty(indexed=False)
    image = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)
    desc = ndb.StringProperty(indexed=False, repeated=True)


class Users(ndb.Model, UserMixin):
    """
    Modello utente
    """
    id = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    serie_list = ndb.KeyProperty(repeated=True)
    special_list = ndb.KeyProperty(repeated=True)
    token = ndb.StringProperty(indexed=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the id to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
