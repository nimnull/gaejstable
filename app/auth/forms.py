# import logging
from flaskext.babel import lazy_gettext as _
from wtforms import (Form, SelectField, TextField, PasswordField,
        validators, ValidationError, HiddenField)

from app import app
from core.validators import Email
from .models import User


class UserBaseForm(Form):
    first_name = TextField(_('First Name'), description=_('enter your first '
            'name here'), validators=[validators.Required()])
    last_name = TextField(_('Last Name'), description=_('enter your last '
            'name here'), validators=[validators.Required()])


class SignInForm(Form):
    username = TextField(_('Email'), description=_('enter your email '
            'address to sign in'), validators=[Email()])
    password = PasswordField(_('Password'), description=_('provide your '
            'password to authenticate yourself'), validators=[
                validators.Required(message=_("We can't proceed without "
                    "password"))])


class SignUpForm(UserBaseForm, SignInForm):
    confirm = PasswordField(_('Confirm Password'), description=_('repeat your '
            'password entered above'), validators=[
                validators.EqualTo('password', message=_('Passwords must match'))])

    def validate_username(self, field):
        if not User.is_unique(field.data):
            raise ValidationError(_('this email has already taken'))

    def save(self):
        user_data = self.data
        del user_data['confirm']
        return User.create(**user_data)


class ProfileForm(UserBaseForm):
    language = SelectField(_('language'), description=_('select '
        'locale', choice=app.config['LANGUAGES']))


class AskRecoverForm(Form):
    email = TextField(_('Email'), description=_('enter your email to get '
                'password reset link'), validators=[Email()])

    def validate_email(self, field):
        if User.is_unique(field.data):
            raise ValidationError(_('This user is not registered'))

    def get_user(self):
        return User.get_by_email(self.email.data)


class PasswordResetForm(Form):
    password = PasswordField(_('New Password'), description=_('enter new '
                'password'), validators=[validators.Required(),
                    validators.EqualTo('confirm')])
    confirm = PasswordField(_('Confirm New Password'), description=_('repeat '
                'password entered above'))
    token = HiddenField(validators=[validators.Required()])

    def save(self):
        user = User.validate_token(self.token.data)
        if user:
            user.set_password(self.password.data).put_async()
        return user
