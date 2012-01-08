import logging
from flask import request, redirect, url_for

from core.decorators import render_to

from . import auth
from .forms import SignUpForm, SignInForm
from .models import User


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
            return redirect(url_for('core.index'))
        else:
            # have to add flash message creation/rendering
            pass
    return {'form': form}


@auth.route('/sign_out')
@render_to()
def sign_out():
    return {}


@auth.route('/sign_in')
@render_to()
def recover():
    return {}


@auth.route('/profile/<key>')
@render_to()
def profile(key):
    user = User.get_by_urlsafe(key)
    return {'user': user}
