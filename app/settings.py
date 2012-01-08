import os

DIRNAME = os.path.dirname(__file__)

DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

SECRET_KEY = '<D=f1^F%w8Xr/9?^KR+sYhEOZx8X9jZd3Zdi8)r);F/}\@Stg['

SITE_TITLE = 'GAE JS Table'

EMAIL_FROM = 'Gaejs <do-not-reply@gmail.com>'

ASSETS_DIRECTORY = os.path.join(DIRNAME, 'static')
ASSETS_URL = "/static/"
ASSETS_CLOSURE_COMPRESSOR_OPTIMIZATION = 'ADVANCED_OPTIMIZATIONS'
ASSETS_UPDATER = False
ASSETS_EXPIRE = False
YUI_COMPRESSOR_PATH = "/home/nimnull/bin/yuicompressor.jar"
COMPASS_BIN = "/usr/local/bin/compass"
COMPASS_PLUGINS = ['compass_twitter_bootstrap']
