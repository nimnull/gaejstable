
from auth.decorators import login_required
from . import core
from .decorators import render_to


@core.route('/')
@login_required
@render_to()
def index():
    return {}
