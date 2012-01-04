import urllib

from flask import Blueprint, request

from app import app


core = Blueprint('core', __name__, template_folder='templates')


def url_for_other_page(page):
    args = request.args.copy()
    args['page'] = page
    return '?' + urllib.urlencode(args)


@app.context_processor
def inject():
    return dict(url_for_other_page=url_for_other_page)
