
from auth.decorators import login_required
from . import core
from .decorators import render_to


@login_required
@core.route('/')
@render_to("core/index.html")
def index():
    return {}
