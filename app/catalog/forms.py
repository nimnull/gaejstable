from wtforms import (Form, TextField, validators)

from .models import Category


class CategoryForm(Form):
    title = TextField('Title', description='category title',
            validators=[validators.Required()])

    def save(self, request=None):
        return Category.create({'en': self.title.data})
