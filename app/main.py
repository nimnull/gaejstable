import os
import sys
# import logging


DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')


# Add lib as primary libraries directory, with fallback to lib/dist
# and optionally to lib/dist.zip, loaded using zipimport.
lib_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib')
if lib_path not in sys.path:
    sys.path[0:0] = [
        lib_path,
    ]

from werkzeug_debugger_appengine import get_debugged_app

from app import app


def enable_appstats(app):
    """Enables appstats middleware."""
    from google.appengine.ext.appstats.recording import \
        appstats_wsgi_middleware
    app.wsgi_app = appstats_wsgi_middleware(app.wsgi_app)


def enable_jinja2_debugging():
    """Enables blacklisted modules that help Jinja2 debugging."""
    from google.appengine.tools.dev_appserver import HardenedModulesHook
    HardenedModulesHook._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']


#enable_appstats(app)
if app.debug:
    app = get_debugged_app(app)
    enable_jinja2_debugging()
