from flask import g, url_for, redirect, request
from functools import wraps


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.sign_in', next=request.url))
        else:
            return f(*args, **kwargs)
    return wrapper
