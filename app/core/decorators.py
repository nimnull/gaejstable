# import logging

from functools import wraps

from flask import request, abort


def json_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'application/json' not in request.headers.get('Accept', ''):
            abort(400)
        return func(*args, **kwargs)
    return wrapper
