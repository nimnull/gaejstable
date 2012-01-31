import os
_ = lambda s: s

DIRNAME = os.path.dirname(__file__)

DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

SECRET_KEY = '<D=f1^F%w8Xr/9?^KR+sYhEOZx8X9jZd3Zdi8)r);F/}\@Stg['

SESSION_COOKIE_NAME = '_gaejst'
PERMANENT_SESSION_LIFETIME = 432000

SITE_TITLE = 'GAE JS Table'

EMAIL_FROM = 'Gaejs <do-not-reply@gmail.com>'

ASSETS_DIRECTORY = os.path.join(DIRNAME, 'static')
ASSETS_URL = "/static/"
ASSETS_CLOSURE_COMPRESSOR_OPTIMIZATION = 'ADVANCED_OPTIMIZATIONS'
ASSETS_UPDATER = False
ASSETS_EXPIRE = False

YUI_COMPRESSOR_PATH = "/home/nimnull/bin/yuicompressor.jar"

CLOSURE_COMPRESSOR_PATH = "/home/nimnull/bin/compiler.jar"

COMPASS_BIN = "/usr/local/bin/compass"
COMPASS_PLUGINS = ['compass_twitter_bootstrap']

BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'
DEFAULT_LANGUAGE = BABEL_DEFAULT_LOCALE
LANGUAGES = {
        'en': 'English',
        'ru': 'Russian'
}
ADMINS = ['nimnull@gmail.com', 'd.fedorishev@gmail.com']

SITEMAP = {
    'core.index': {
        'title': _('Main'),
        'children': {
            'catalog.list_categories': {
                'children': {
                    'catalog.create_category': {},
                    'catalog.create_record': {},
                    'catalog.list_records': {},
                }
            },
            'catalog.filtered_records': {
                'children': {
                    'catalog.selected_records': {},
                    'catalog.tagged_records': {},
                }
            },
            'auth.profile': {
                'children': {
                    'auth.edit_profile': {},
                    'auth.setup_profile': {},
                }
            },
            'auth.sign_up': {
                'children': {
                    'auth.activate': {}
                }
            },
            'auth.sign_in': {},
            'auth.sign_out': {},
            'auth.ask_recovery': {
                'children': {
                    'auth.finish_recovery': {}
                }
            },
        },
    }
}
