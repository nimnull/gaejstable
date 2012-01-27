import logging
from flask import g, session

from app import app
from .models import User


@app.before_request
def populate_current_user(*args, **kwargs):
    g.user = None
    uid_safe = session.get('uid')
    if uid_safe is None:
        return
    try:
        user = User.get_by_urlsafe(uid_safe)
        if user is not None:
            g.user = user
    except (AttributeError, TypeError), e:
        logging.info(e)
