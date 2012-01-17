# import logging
from wtforms import (Form, TextField, PasswordField, validators,
    ValidationError, HiddenField)
# from wtforms.ext.csrf.session import SessionSecureForm

from core.validators import Email

from .models import User


class ProfileForm(Form):
    first_name = TextField('First Name', description='enter your first '
            'name here', validators=[validators.Required()])
    last_name = TextField('Last Name', description='enter your last '
            'name here', validators=[validators.Required()])


class SignInForm(Form):
    username = TextField('Email', description='enter your email '
            'address to sign in', validators=[Email()])
    raw_password = PasswordField('Password', description='provide your '
            'password to authenticate yourself', validators=[
                validators.Required(message="We can't proceed without "
                    "password")])


class SignUpForm(ProfileForm):
    username = TextField('Your Email', description='email will acts as your login',
            validators=[Email()])
    password = PasswordField('New Password', description='chose a '
            'password for signing in', validators=[
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', description='repeat your '
            'password entered above')

    def validate_username(self, field):
        if not User.is_unique(field.data):
            raise ValidationError('this email has already taken')

    def save(self):
        user_data = self.data
        del user_data['confirm']
        return User.create(**user_data)


class AskRecoverForm(Form):
    email = TextField('Email', description='enter your email to get '
                'password reset link', validators=[Email()])

    def validate_email(self, field):
        if User.is_unique(field.data):
            raise ValidationError('This user is not registered')

    def get_user(self):
        return User.get_by_email(self.email.data)


class PasswordResetForm(Form):
    password = PasswordField('New Password', description='enter new '
                'password', validators=[validators.Required(),
                    validators.EqualTo('confirm')])
    confirm = PasswordField('Confirm New Password', description='repeat '
                'password entered above')
    token = HiddenField(validators=[validators.Required()])

    def save(self):
        user = User.validate_token(self.token.data)
        if user:
            user.set_password(self.password.data).put_async()
        return user
