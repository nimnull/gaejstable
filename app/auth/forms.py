from wtforms import Form, TextField, PasswordField, validators


class SignUpForm(Form):
    email = TextField('Email', description='email will be used as your login',
            validators=[validators.Length(min=6, max=35)])
    password = PasswordField('New Password', description='chose a '
            'password for signing in', validators=[
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', description='repeat your '
            'password entered above')

    def save(self):
        pass
