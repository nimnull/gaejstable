from core.decorators import render_to
from . import auth


@auth.route('/sign_up')
@render_to("auth/sign_up.html")
def sign_up():
    return {}


@auth.route('/sign_in')
@render_to("auth/sign_in.html")
def sign_in():
    return {}


@auth.route('/sign_out')
@render_to("auth/sign_out.html")
def sign_out():
    return {}


@auth.route('/sign_in')
@render_to("auth/recover.html")
def recover():
    return {}
