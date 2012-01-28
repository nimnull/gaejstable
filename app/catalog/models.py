# import logging
from flask import g
from ndb import context, key, model, tasklets

from app import app

from auth.models import User

from core.models import LangValue, Unique, PagedMixin, LocalPagedMixin
from core.slugify import get_unique_slug


class Category(model.Model, LocalPagedMixin):
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
        title = title_dict.get(app.config['BABEL_DEFAULT_LOCALE']) or \
            title_dict.keys()[0]
        return get_unique_slug(cls, title, Unique)

    @property
    def selected(self):
        return True if User2Category.relations(g.user, self).get() is not None else False


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
        return cls.create_async(user, category).get_result().get()

    @classmethod
    def create_async(cls, user, category):
        return cls(user=user.key, category=category.key).put_async()

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


class Record(model.Model, LocalPagedMixin):
    title_s = model.StructuredProperty(LangValue, repeated=True)
    description_s = model.StructuredProperty(LangValue, repeated=True)
    created_at = model.DateTimeProperty(auto_now_add=True)
    category = model.KeyProperty(kind=Category)
    tags = model.StructuredProperty(LangValue, repeated=True)

    @property
    def local_tags(self):
        return [tag.value for tag in self.tags if tag.lang == g.lang]

    @property
    @context.toplevel
    def is_marked(self):
        relations = yield User2Record.relations(g.user, self).get_async()
        raise tasklets.Return(relations)

    @classmethod
    def for_category(cls, category):
        if isinstance(category, unicode):
            category = key.Key(urlsafe=category)
        elif isinstance(category, Category):
            category = category.key
        return cls.query(cls.category == category)

    @classmethod
    def for_categories(cls, categories):
        return cls.query(cls.category.IN(categories)).order(
                -cls.key, -cls.created_at)

    @classmethod
    def create(cls, locale_dict, category, tags_dict):
        tags = [LangValue(lang=lang, value=tag) for lang, tags
                in tags_dict.iteritems() for tag in tags]

        if isinstance(category, unicode):
            cat_key = key.Key(urlsafe=category)
        else:
            cat_key = category.key
        kwargs = {'category': cat_key, 'tags': tags}
        for lang, values in locale_dict.iteritems():
            for field, value in values.iteritems():
                field_list = kwargs.get('%s_s' % field, [])
                field_list.append(LangValue(lang=lang, value=value))
                kwargs['%s_s' % field] = field_list
        return Record(**kwargs).put().get()


class User2Record(model.Model, PagedMixin):
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
