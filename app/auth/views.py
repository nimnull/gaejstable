import logging
from flask import flash, g, request, redirect, session, url_for

from core.decorators import render_to

from . import auth
from .decorators import login_required
from .forms import SignUpForm, SignInForm
from .models import User
from .utils import login, logout


@auth.route('/sign_up', methods=['GET', 'POST'])
@render_to()
def sign_up():
    form = SignUpForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        key = form.save()
        return redirect(url_for('auth.profile', key=key.urlsafe()))
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


@auth.route('/recover')
@render_to()
def recover():
    form = object()
    if request.method == 'POST' and form.validate():
        user = User.query(User.username==form.email.data).get()
        if user is not None:
            user.propagate(is_active=False, recover_url='')
            user.put()
            return {'recover_sent': True}
    return {'form': form}


@auth.route('/profile')
@login_required
@render_to()
def profile():
    return {'user': g.user}
