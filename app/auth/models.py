# import logging
import random
from datetime import datetime
from ndb import model
from time import mktime

from app import app
from .utils import get_hexdigest


class User(model.Model):
    DEFAULT_LOCALE = app.config['BABEL_DEFAULT_LOCALE']
    DEFAULT_TIMEZONE = app.config['BABEL_DEFAULT_TIMEZONE']
    LANG_CHOICES = app.config['LANGUAGES'].keys()
    username = model.StringProperty(required=True, indexed=True)
    password = model.StringProperty(required=True)
    first_name = model.StringProperty(required=True)
    last_name = model.StringProperty(required=True)
    created_at = model.DateTimeProperty(auto_now_add=True)
    logged_at = model.DateTimeProperty()
    is_active = model.BooleanProperty(default=False)
    locale = model.StringProperty(default=DEFAULT_LOCALE,
            choices=LANG_CHOICES)

    @classmethod
    def create(cls, username, password, first_name, last_name):
        if cls.is_unique(username):
            newuser = cls(username=username.lower(), first_name=first_name,
                                                        last_name=last_name)
            newuser.set_password(password)
            return newuser.put().get()
        else:
            return None

    @classmethod
    def check_password(cls, username, password):
        user = cls.query(cls.username == username.lower()).get()
        if user is None:
            return False
        algo, salt, hsh = user.password.split('$')
        if hsh == get_hexdigest(algo, salt, password):
            return user
        return False

    @classmethod
    def get_by_urlsafe(self, urlsafe):
        return model.Key(urlsafe=urlsafe).get()

    @classmethod
    def get_by_email(cls, email):
        return cls.query(cls.username == email).get()

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
        return self

    def update_login_time(self):
        """ update last logged in time with UTC ts
        for default we'll return an updated User instance
        """
        self.logged_at = datetime.utcnow()
        return self.put().get()

    def create_token(self):
        """ creates a unique token based on user last login time and
        urlsafe encoded user key
        """
        ts_datetime = self.logged_at or self.created_at
        ts = int(mktime(ts_datetime.timetuple()))
        base = "{}{}".format(self.key.urlsafe(), ts)
        algo, salt, pass_hash = self.password.split('$')
        return "{}$${}".format(self.key.urlsafe(), get_hexdigest(algo, salt, base))

    @classmethod
    def validate_token(cls, token):
        if token is not None:
            key_safe, hsh = token.split('$$')
            user = cls.get_by_urlsafe(key_safe)
            return token == user.create_token() and user
        return False
