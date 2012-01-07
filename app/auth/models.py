import random
from ndb import model

from auth.utils import get_hexdigest


class User(model.Model):
    username = model.StringProperty(required=True, indexed=True)
    password = model.StringProperty(required=True)
    first_name = model.StringProperty(required=True)
    last_name = model.StringProperty(required=True)
    created_at = model.DateTimeProperty(auto_now_add=True)

    @classmethod
    def create(cls, username, password, first_name, last_name):
        if cls.__is_unique(username):
            newuser = cls(username=username, first_name=first_name,
                                                        last_name=last_name)
            newuser.set_password(password)
            return newuser().put()
        else:
            return None

    @classmethod
    def __is_unique(cls, username):
        count = cls.query(cls.username == username.lower()).count()
        return count == 0

    def set_password(self, raw_password):
        algo = 'sha1'
        rand_str = lambda: str(random.random())
        salt = get_hexdigest(algo, rand_str(), rand_str())[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)
