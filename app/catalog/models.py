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
        assert isinstance(title_dict, (dict))
        title_set = [LangValue(lang=lang_code, value=value)
            for lang_code, value in title_dict.items()]
        return cls(title_s=title_set, slug=cls.__get_slug(title_dict)).put().get()

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
    def paginate_categories(cls, page_size=20):
        def localize(cat):
            for lv in cat.title_s:
                if lv.lang == g.lang:
                    setattr(cat, 'title', lv.value)
            return cat
        q = cls.get_localized(g.lang)
        pager = Pager(query=q)
        categories, _, _ = pager.paginate(page_size)
        categories = map(localize, categories)
        return categories, pager

    @property
    def selected(self):
        return True if User2Category.get(g.user, self) is not None else False


class User2Category(model.Model):
    from auth.models import User
    user = model.KeyProperty(kind=User)
    category = model.KeyProperty(kind=Category)

    @classmethod
    def get_for_user(cls, user):
        pass

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
