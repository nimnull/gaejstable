import logging
from flask import (flash, g, request, redirect, render_template,
    session, url_for)

from google.appengine.api import app_identity, mail

from settings import SITE_TITLE

from core.decorators import render_to

from . import auth
from .decorators import login_required
from .forms import SignUpForm, SignInForm, AskRecoverForm
from .models import User
from .utils import login, logout


@auth.route('/sign_up', methods=['GET', 'POST'])
@render_to()
def sign_up():
    form = SignUpForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        user = form.save()
        login(user)
        return redirect(url_for('auth.profile', key=user.key.urlsafe()))
    return {'form': form}


@auth.route('/sign_in', methods=['GET', 'POST'])
@render_to()
def sign_in():
    if request.args.get('next'):
        session['next'] = request.args['next']
    form = SignInForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        user = User.check_password(**form.data)
        if user:
            login(user)
            if session.get('next'):
                return redirect(session['next'])
            else:
                return redirect(url_for('core.index'))
        else:
            flash('There is no user with provided email or password',
                        category='warning')
            return redirect(url_for('auth.sign_in'))
    return {'form': form}


@auth.route('/sign_out')
@login_required
@render_to()
def sign_out():
    logout()
    return redirect(url_for('core.index'))


@auth.route('/recover', methods=['GET', 'POST'])
@render_to()
def recover_ask():
    form = AskRecoverForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        user = form.get_user()
        token = user.create_token()
        app_hostname = app_identity.get_default_version_hostname()
        email = {
            'sender': "Mail robot on {} <no-reply@{}>".format(SITE_TITLE,
                app_hostname),
            'to': user.username,
            'subject': "Password recovery for {}".format(SITE_TITLE),
            'body': render_template('auth/recover_email.html',
                token=token, user=user,
                hostname=app_hostname)
        }
        mail.send_mail(**email)
        logging.info(email['body'])
        flash("We've just sent an email to <strong>{}</strong> with "
              "the special link for you to reset lost password.".format(
                  user.username), category='success')
        session['recover_sent'] = True
        session.permanent = False
        return redirect(url_for('auth.recover_ask'))
    return {'form': form, }


@auth.route('/recover/finish', methods=['GET', 'POST'])
@render_to()
def recover_finish():
    logging.info(request.args)
    return {}


@auth.route('/profile')
@login_required
@render_to()
def profile():
    return {'user': g.user}
