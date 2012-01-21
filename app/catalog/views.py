# import logging
from flask import request, redirect, url_for
from flaskext.babel import get_locale
from auth.decorators import login_required

from core.decorators import render_to
from . import catalog
from .forms import CategoryForm
from .models import Category


@catalog.route('/cats/create', methods=['GET', 'POST'])
@login_required
@render_to()
def create_category():
    form = CategoryForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        form.save()
        return redirect(url_for('.list_categories'))
    return {'form': form}


@catalog.route('/cats')
@render_to()
def list_categories():
    cats_q = Category.get_localized(get_locale().language)
    return {'query': cats_q}
