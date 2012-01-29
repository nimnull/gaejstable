from flask import g
from flaskext.babel import lazy_gettext as _
from wtforms import (Form, FileField, HiddenField, TextAreaField,
        TextField, validators)

from .models import Category, Record


class CategoryForm(Form):
    title = TextField(_('Title'), description=_('category title'),
            validators=[validators.Required()])

    def save(self, request=None):
        return Category.create({g.lang: self.title.data})


class RecordForm(Form):
    title = TextField(_('Title'), description=_('enter title for record'),
            validators=[validators.Required()])
    description = TextAreaField(_('Description'), description=_('enter title '
        'for record'), validators=[validators.Required()])
    category = HiddenField(validators=[validators.Required()])
    tags = TextField(_('Tags', description=_('enter tags separated by '
        'commas')))
    attachment = FileField(_('Atachment'))

    def save(self, attachment):
        tags = [item.strip() for item in  self.tags.data.split(',')]
        return Record.create({
            g.lang: {'title': self.title.data,
                     'description': self.description.data}},
            self.category.data,
            tags_dict={g.lang: tags},
            attachment=attachment)
