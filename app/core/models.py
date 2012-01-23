from ndb import model

from app import app


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
    value = model.StringProperty(required=True)


class Unique(model.Model):

    @classmethod
    def create(cls, value):
        entity = cls(key=model.Key(cls, value))
        txn = lambda: entity.put() if not entity.key.get() else None
        return model.transaction(txn) or None
