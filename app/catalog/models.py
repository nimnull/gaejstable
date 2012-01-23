from flask import g
from ndb import model, key

from app import app
from core.models import LangValue, Unique
from core.pagination import Pager
from core.slugify import get_unique_slug


class Category(model.Model):
    slug = model.StringProperty(required=True)
    title_s = model.StructuredProperty(LangValue, repeated=True)

    @classmethod
    def create(cls, title_dict):
        title_set = [LangValue(lang=lang_code, value=value)
            for lang_code, value in title_dict.items()]
        return cls(title_s=title_set, slug=cls.__get_slug(title_dict)).put().get()

    @classmethod
    def get(cls, key):
        return cls.get_async(key).get_result()

    @classmethod
    def get_async(cls, cat_key):
        if isinstance(cat_key, (str, unicode)):
            cat_key = key.Key(urlsafe=cat_key)
        return cat_key.get_async()

    @classmethod
    def get_by_urlsafe(cls, urlsafe):
        return key.Key(urlsafe=urlsafe).get()

    @classmethod
    def __get_slug(cls, title_dict):
        title = title_dict.get(app.config['DEFAULT_LANGUAGE']) or \
            title_dict.keys()[0]
        return get_unique_slug(cls, title, Unique)

    @classmethod
    def get_localized(cls, lang_code):
        return cls.query(cls.title_s.lang == lang_code)

    @classmethod
    def paginate(cls, query=None, page_size=20):
        q = query or cls.get_localized(g.lang)
        pager = Pager(query=q)
        categories, _, _ = pager.paginate(page_size)
        return categories, pager

    @property
    def selected(self):
        return True if User2Category.get(g.user, self) is not None else False

    def __getattr__(self, name):
        attr_s = getattr(self, '%s_s' % name)
        lvs = filter(lambda lv: lv.lang == g.lang, attr_s)
        return len(lvs) and lvs[0].value or ''


class User2Category(model.Model):
    from auth.models import User
    user = model.KeyProperty(kind=User)
    category = model.KeyProperty(kind=Category)

    @classmethod
    def get_for_user(cls, user):
        return cls.query(cls.user == user.key)

    @classmethod
    def get(cls, user, category):
        return cls.query(cls.user == user.key,
                         cls.category == category.key).get()

    @classmethod
    def create(cls, user, category):
        return cls(user=user.key, category=category.key).put().get()

    @classmethod
    def get_or_create(cls, user, category):
        entity = cls.get(user, category)
        if entity is not None:
            return entity, False
        else:
            return cls.create(user, category), True

    @classmethod
    def delete(cls, user, category):
        entity = cls.get_by_user2cat(user, category)
        if entity is not None:
            entity.key.delete_async()
            return True
        return False


class Record(model.Model):
    title_s = model.StructuredProperty(LangValue, repeated=True)
    description_s = model.StructuredProperty(LangValue, repeated=True)
    created_at = model.DateTimeProperty(auto_now_add=True)
    category = model.KeyProperty(kind=Category)

    def __getattr__(self, name):
        attr_s = getattr(self, '%s_s' % name)
        lvs = filter(lambda lv: lv.lang == g.lang, attr_s)
        return len(lvs) and lvs[0].value or ''

    @classmethod
    def for_category(cls, category):
        if isinstance(category, (str, unicode)):
            cat_key = key.Key(urlsafe=category)
        elif isinstance(category, Category):
            cat_key = category.key
        elif isinstance(category, key.Key):
            cat_key = category
        else:
            raise TypeError("Invalid 'category' argument type")
        return cls.query(cls.category == cat_key)

    @classmethod
    def for_categories(cls, categories):
        return cls.query(cls.category.IN(categories)).order(
                -cls.key, -cls.created_at)

    @classmethod
    def paginate(cls, query=None, page_size=20):
        pager = Pager(query=query)
        records, _, _ = pager.paginate(page_size)
        return records, pager

    @classmethod
    def create(cls, title, description, category):
        if isinstance(category, (str, unicode)):
            cat_key = key.Key(urlsafe=category)
        else:
            cat_key = category.key
        entity = Record(title_s=[LangValue(lang=g.lang, value=title)],
               description_s=[LangValue(lang=g.lang, value=description)],
               category=cat_key)
        return entity.put().get()
