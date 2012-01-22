import logging
from google.appengine.ext.ndb import context, tasklets

from flask import request, redirect, url_for, render_template
from flaskext.babel import get_locale

from auth.decorators import login_required

from core.decorators import render_to
from core.pagination import Pager
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
@login_required
@context.toplevel
def list_categories():
    lang_code = get_locale().language
    cats_q = Category.get_localized(lang_code)
    res = yield _list_categories(cats_q, lang_code)
    raise tasklets.Return(res)


@tasklets.tasklet
def _list_categories(cats_q, lang_code):
    def localize(cat):
        for lv in cat.title:
            if lv.lang == lang_code:
                setattr(cat, 'l_title', lv.value)
        return cat
    pager = Pager(query=cats_q)
    categories, _, _ = pager.paginate()
    categories = map(localize, categories)
    logging.info(categories)

    ctx = {'pager': pager, 'categories': categories}

    raise tasklets.Return(render_template('catalog/list_categories.html', **ctx))
