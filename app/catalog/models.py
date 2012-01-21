from google.appengine.ext.ndb import model

from core.models import LangValue


class Category(model.Model):
    slug = model.StringProperty(requred=True)
    title = model.StructuredProperty(LangValue, repeated=True)

    @classmethod
    def create(cls, title_dict):
        assert isinstance(title_dict, (dict))
        title_set = [LangValue(lang=lang_code, value=value)
            for lang_code, value in title_dict.items()]
        return cls(title=title, title=title_set).put().get()
