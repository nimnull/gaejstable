from flask import redirect, url_for
from auth.decorators import login_required
from . import core


@core.route('/')
@login_required
def index():
    return redirect(url_for('catalog.filtered_records'))
