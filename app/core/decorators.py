# import logging

from functools import wraps

from flask import request, abort, render_template


def json_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'application/json' not in request.headers.get('Accept', ''):
            abort(400)
        return func(*args, **kwargs)
    return wrapper


def render_to(template):
    def wrapper(f):
        @wraps(f)
        def callback(*args, **kwargs):
            response = f(*args, **kwargs)
            if isinstance(response, dict):
                return render_template(template, **response)
            else:
                return response
        return callback
    return wrapper
