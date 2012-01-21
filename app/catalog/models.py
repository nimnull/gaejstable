from google.appengine.ext.ndb import model

from app import app
from core.models import LangValue, Unique
from core.slugify import get_unique_slug


class Category(model.Model):
    slug = model.StringProperty(required=True)
    title = model.StructuredProperty(LangValue, repeated=True)

    @classmethod
    def create(cls, title_dict):
        assert isinstance(title_dict, (dict))
        title_set = [LangValue(lang=lang_code, value=value)
            for lang_code, value in title_dict.items()]
        return cls(title=title_set, slug=cls.__get_slug(title_dict)).put().get()

    @classmethod
    def __get_slug(cls, title_dict):
        title = title_dict.get(app.config['DEFAULT_LANGUAGE']) or \
            title_dict.keys()[0]
        return get_unique_slug(cls, title, Unique)

    @classmethod
    def get_localized(cls, lang_code):
        return cls.query(cls.title.lang == lang_code)
