from flask import g, request
from flaskext.babel import get_locale

from app import app, babel


@babel.localeselector
def locale():
    user = getattr(g, 'user', None)
    if user is None:
        return request.accept_languages.best_match(
                app.config['LANGUAGES'].keys())
    else:
        return user.locale


@app.before_request
def populate_locale(*args, **extra):
    g.lang = get_locale().language
