# import logging
from wtforms import (Form, TextField, PasswordField, validators,
    ValidationError)
# from wtforms.ext.csrf.session import SessionSecureForm

from core.validators import Email

from .models import User


class SignInForm(Form):
    username = TextField('Email', description='enter your email '
            'address to sign in', validators=[Email()])
    raw_password = PasswordField('Password', description='provide your '
            'password to authenticate yourself', validators=[
                validators.Required(message="We can't proceed without "
                    "password")])


class SignUpForm(Form):
    first_name = TextField('First Name', description='enter your first '
            'name here', validators=[validators.Required()])
    last_name = TextField('Last Name', description='enter your last '
            'name here', validators=[validators.Required()])
    username = TextField('Your Email', description='email will acts as your login',
            validators=[Email()])
    password = PasswordField('New Password', description='chose a '
            'password for signing in', validators=[
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', description='repeat your '
            'password entered above')

    def validate_username(self, field):
        if not User.is_unique(self.username.data):
            raise ValidationError('this email has already taken')

    def save(self):
        user_data = self.data
        del user_data['confirm']
        return User.create(**user_data)
