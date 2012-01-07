# import logging
from flask import Flask, render_template
# from flaskext.principal import Principal
# from flaskext.babel import Babel
from flaskext.assets import Environment
from core.assets import AppEngineBundle
from core import core
from auth import auth, set_current_user
from auth.models import User
# principal = Principal(app)
# babel = Babel(app)
app = Flask(__name__)
app.config.from_object('settings')
assets = Environment(app)

css = AppEngineBundle(
    'chosen/chosen.css',
    'stylesheets/screen.css',
    filters=['cssrewrite', 'yui_css'],
    output='gen/packed.css')
assets.register('css_all', css)

js = AppEngineBundle(
    AppEngineBundle(
        'bootstrap/bootstrap-modal.js',
        'bootstrap/bootstrap-twipsy.js',
        'jquery-placeholder/jquery.placeholder.js',
        'chosen/chosen.jquery.js',
    ),
    AppEngineBundle(
        'coffee/aform.coffee',
        'coffee/scripts.coffee',
        'coffee/commenting.coffee',
        'coffee/voting.coffee',
        'coffee/queries.coffee',
        'coffee/query-create.coffee',
        filters='coffeescript',
    ),
    # filters='closure_js',
    output='gen/packed.js')
assets.register('js_all', js)




app.register_blueprint(core)
app.register_blueprint(auth)


# @app.before_request
# def lookup_current_user():
#     set_current_user(User.get_current_user())


_missing = object()


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
