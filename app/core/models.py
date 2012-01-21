from flask import app
from google.appengine.ext.ndb import model


LANG_CHOICES = app.config.get('LANGUAGES', ['en'])
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
    lang = model.StringProperty(required=True, choices=LANG_CHOICES)
    value = model.StringProperty(required=True)
