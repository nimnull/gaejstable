from core.decorators import render_to
from . import auth


@auth.route('/sign_up')
@render_to()
def sign_up():
    return {}


@auth.route('/sign_in')
@render_to()
def sign_in():
    return {}


@auth.route('/sign_out')
@render_to()
def sign_out():
    return {}


@auth.route('/sign_in')
@render_to()
def recover():
    return {}
