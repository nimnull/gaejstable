import logging
from flask import g, request_started, session

from app import app
from .models import User


def populate_current_user(sender, **extra):
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

request_started.connect(populate_current_user, app)
