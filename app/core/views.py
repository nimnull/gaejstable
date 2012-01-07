from . import core
from .decorators import render_to


@render_to("core/index.html")
@core.route('/')
def index():
    return {}
