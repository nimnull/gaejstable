# import logging
from flask import g
from ndb import context, key, model, tasklets

from app import app

from auth.models import User

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
        if isinstance(cat_key, unicode):
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
        return True if User2Category.relations(g.user, self).get() is not None else False

    def __getattr__(self, name):
        attr_s = getattr(self, '%s_s' % name)
        lvs = filter(lambda lv: lv.lang == g.lang, attr_s)
        return len(lvs) and lvs[0].value or ''


class User2Category(model.Model):
    user = model.KeyProperty(kind=User)
    category = model.KeyProperty(kind=Category)

    @classmethod
    def get_for_user(cls, user):
        return cls.query(cls.user == user.key)

    @classmethod
    def relations(cls, user, category):
        return cls.query(cls.user == user.key,
                         cls.category == category.key)

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

    @property
    @context.toplevel
    def is_marked(self):
        relations = yield User2Record.relations(g.user, self).get_async()
        raise tasklets.Return(relations)

    @classmethod
    def for_category(cls, category):
        if isinstance(category, unicode):
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
        if isinstance(category, unicode):
            cat_key = key.Key(urlsafe=category)
        else:
            cat_key = category.key
        entity = Record(title_s=[LangValue(lang=g.lang, value=title)],
               description_s=[LangValue(lang=g.lang, value=description)],
               category=cat_key)
        return entity.put().get()


class User2Record(model.Model):
    user = model.KeyProperty(kind=User)
    record = model.KeyProperty(kind=Record)

    @classmethod
    def _create(cls, user, record):
        if isinstance(record, Record):
            record = record.key
        elif isinstance(record, unicode):
            record = key.Key(urlsafe=record)
        if isinstance(user, User):
            user = user.key
        return cls(user=user, record=record).put_async()

    create_async = _create

    @classmethod
    def create(cls, user, record):
        return cls.create_async(user, record).get_result()

    @classmethod
    def relations(cls, user, record=None):
        if isinstance(user, User):
            user = user.key
        if record is None:
            return cls.query(cls.user == user)
        else:
            if isinstance(record, Record):
                record = record.key
            elif isinstance(record, unicode):
                record = key.Key(urlsafe=record)
            return cls.query(cls.user == user, cls.record == record)

    @classmethod
    @context.toplevel
    def delete(cls, user, record):
        raise tasklets.Return(cls._delete(user, record))

    @classmethod
    @tasklets.tasklet
    def _delete(cls, user, record):
        if isinstance(record, Record):
            record = record.key
        elif isinstance(record, unicode):
            record = key.Key(urlsafe=record)
        if isinstance(user, User):
            user = user.key
        q = cls.query(cls.user == user, cls.record == record)
        entity = yield q.get_async()
        if entity is not None:
            entity.key.delete_async()
