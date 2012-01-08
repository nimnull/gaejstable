import logging
import random
from google.appengine.ext.ndb import model

from .utils import get_hexdigest


class User(model.Model):
    username = model.StringProperty(required=True, indexed=True)
    password = model.StringProperty(required=True)
    first_name = model.StringProperty(required=True)
    last_name = model.StringProperty(required=True)
    created_at = model.DateTimeProperty(auto_now_add=True)

    @classmethod
    def create(cls, username, password, first_name, last_name):
        if cls.is_unique(username):
            newuser = cls(username=username.lower(), first_name=first_name,
                                                        last_name=last_name)
            newuser.set_password(password)
            return newuser.put()
        else:
            return None

    @classmethod
    def check_password(cls, username, raw_password):
        user = cls.query(cls.username == username.lower()).get()
        logging.info(user)
        if user is None:
            return False
        algo, salt, hsh = user.password.split('$')
        if hsh == get_hexdigest(algo, salt, raw_password):
            return user
        return False

    @classmethod
    def get_by_urlsafe(self, urlsafe):
        return model.Key(urlsafe=urlsafe).get()

    @classmethod
    def is_unique(cls, username):
        count = cls.query(cls.username == username.lower()).count()
        return count == 0

    def set_password(self, raw_password):
        algo = 'sha1'
        rand_str = lambda: str(random.random())
        salt = get_hexdigest(algo, rand_str(), rand_str())[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '{}${}${}'.format(algo, salt, hsh)
