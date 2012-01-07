from core.decorators import render_to
from . import auth


@render_to("auth/register.html")
@auth.route('/register')
def register():
    return {}


@render_to("auth/recover.html")
@auth.route('/sign_in')
def recover():
    return {}


@render_to("auth/sign_in.html")
@auth.route('/sign_in')
def sign_in():
    return {}


@render_to("auth/sign_out.html")
@auth.route('/sign_out')
def sign_out():
    return {}
