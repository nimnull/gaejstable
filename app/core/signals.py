from flask import g, request_started
from flaskext.babel import get_locale

from app import app


def populate_locale(sender, **extra):
    g.lang = get_locale().language


request_started.connect(populate_locale, app)
