from flask import request, session


def get_next_path(default='/'):
    if 'next' in request.values:
        return request.values['next']
    elif 'next' in session:
        next = session.pop('next')
        return next
    elif request.referrer:
        return request.referrer
    else:
        return default
