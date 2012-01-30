from flask import g
from ndb import model

from app import app
from .pagination import Pager
from .validators import strip_validator


LANG_CHOICES = app.config['LANGUAGES']
# class LangModelMixin(object):
#     langs = model.StringPropertyMixin()
#
#     def has_lang(self, lang_code):
#         return self.lang == lang_code
#
#     @classmethod
#     def get_with_lang(cls, lang_code):
#         return cls.query(cls.langs == lang_code)


class LangValue(model.Model):
    lang = model.StringProperty(required=True,
            choices=LANG_CHOICES.keys())
    tevalue = model.TextProperty(required=True,
            validator=strip_validator)


class Unique(model.Model):

    @classmethod
    def create(cls, value):
        entity = cls(key=model.Key(cls, value))
        txn = lambda: entity.put() if not entity.key.get() else None
        return model.transaction(txn) or None


class PagedMixin(object):

    @classmethod
    def _paginate(cls, query, page_size=20):
        pager = Pager(query=query)
        entities, _, _ = pager.paginate(page_size)
        return entities, pager

    paginate = _paginate


class LocalPagedMixin(PagedMixin):

    @classmethod
    def get_localized(cls, lang_code):
        return cls.query(cls.title_s.lang == lang_code)

    @classmethod
    def paginate(cls, query=None, page_size=20):
        q = query or cls.get_localized(g.lang)
        return cls._paginate(q, page_size)

    def __getattr__(self, name):
        attr_s = getattr(self, '%s_s' % name)
        lvs = filter(lambda lv: lv.lang == g.lang, attr_s)
        return len(lvs) and lvs[0].value or ''
