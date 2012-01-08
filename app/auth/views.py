import logging
from flask import abort, flash, g, request, redirect, url_for

from core.decorators import render_to

from . import auth
from .decorators import login_required
from .forms import SignUpForm, SignInForm
from .models import User
from .utils import login


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
    form = SignInForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        user = User.check_password(**form.data)
        if user:
            login(user)
            return redirect(url_for('core.index'))
        else:
            flash('There is no user with provided email or password', category='warning')
            return redirect(url_for('auth.sign_in'))
    return {'form': form}


@auth.route('/sign_out')
@login_required
@render_to()
def sign_out():
    return {}


@auth.route('/sign_in')
@render_to()
def recover():
    return {}


@auth.route('/profile/<key>')
@login_required
@render_to()
def profile(key):
    if key != g.user.key.urlsafe():
        abort(403)
    user = User.get_by_urlsafe(key)
    return {'user': user}
