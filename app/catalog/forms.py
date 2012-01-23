from wtforms import (Form, HiddenField, TextAreaField, TextField, validators)

from .models import Category, Record


class CategoryForm(Form):
    title = TextField('Title', description='category title',
            validators=[validators.Required()])

    def save(self, request=None):
        return Category.create({'en': self.title.data})


class RecordForm(Form):
    title = TextField('Title', description='enter title for record',
            validators=[validators.Required()])
    description = TextAreaField('Description', description='enter title for record',
            validators=[validators.Required()])
    category = HiddenField(validators=[validators.Required()])

    def save(self):
        return Record.create(self.title.data, self.description.data,
                self.category.data)
