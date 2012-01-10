import logging
from flask import (flash, g, request, redirect, render_template,
    session, url_for)

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
            flash('There is no user with provided email or password', category='warning')
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
def recover():
    form = AskRecoverForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        token = form.make_token()
        email_body = render_template('template_name', token=token)
#    form = object()
#    if request.method == 'POST' and form.validate():
#        user = User.query(User.username==form.email.data).get()
#        if user is not None:
#            user.propagate(is_active=False, recover_url='')
#            user.put()
#            return {'recover_sent': True}
#    return {'form': form}
    return {'form': form}


@auth.route('/profile')
@login_required
@render_to()
def profile():
    return {'user': g.user}
