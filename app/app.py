import urllib
from flask import Flask, render_template, request
from flaskext.babel import Babel


app = Flask(__name__)
app.config.from_object('settings')
babel = Babel(app)

from flaskext.assets import Environment
from core.assets import AppEngineBundle


assets = Environment(app)

css = AppEngineBundle(
    'sass/screen.sass',
    filters=['compass', 'yui_css'],
    output='gen/packed.css')
assets.register('css_all', css)

js = AppEngineBundle(
    AppEngineBundle(
        'javascripts/jquery-1.7.1.min.js',
    ),
    AppEngineBundle(
        'javascripts/bootstrap-alerts.js',
        'javascripts/bootstrap-dropdown.js',
        'javascripts/setup.js',
        filters='closure_js',
    ),
    output='gen/packed.js')
assets.register('js_all', js)

from core import core
from auth import auth
from catalog import catalog


app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(catalog, url_prefix='/cat')
app.register_blueprint(core)
_missing = object()


def url_for_other_page(page):
    args = request.args.copy()
    args['page'] = page
    return '?' + urllib.urlencode(args)


@app.context_processor
def inject():
    return dict(url_for_other_page=url_for_other_page)


@app.template_filter('yesno')
def yesno(value, yes=_missing, no=_missing):
    if value:
        return yes if yes is not _missing else value
    else:
        return no if no is not _missing else value


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def access_denied(e):
    return render_template('403.html'), 403


if __name__ == '__main__':
    app.run()
