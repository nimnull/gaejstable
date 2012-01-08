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


def render_to(template=None):
    def wrapper(f):
        @wraps(f)
        def callback(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = '{}.html'.format(
                        request.endpoint.replace('.', '/'))
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif isinstance(ctx, dict):
                return render_template(template_name, **ctx)
            else:
                return ctx
        return callback
    return wrapper
