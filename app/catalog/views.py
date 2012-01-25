# import logging
from flask import g, jsonify, request, redirect, url_for
from ndb import context, tasklets

from auth.decorators import login_required

from core.decorators import render_to
from . import catalog
from .forms import CategoryForm, RecordForm
from .models import Category, Record, User2Category, User2Record


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
@login_required
@render_to()
def list_categories():
    cats, pager = Category.paginate()
    return {'pager': pager, 'categories': cats}


@catalog.route('/cats/<key>/records/create', methods=['GET'])
@catalog.route('/records/create', methods=['POST'])
@login_required
@render_to()
def create_record(key=None):
    form = RecordForm(len(request.form) and request.form or None,
            category=key)
    if request.method == 'POST' and form.validate():
        form.save()
        return redirect(url_for('.list_records', key=form.category.data))
    else:
        category = Category.get_by_urlsafe(key)
        return {'form': form, 'category': category}


@catalog.route('/cats/<key>/records')
@login_required
@render_to()
@context.toplevel
def list_records(key):
    category = yield Category.get_async(key)
    records, pager = Record.paginate(Record.for_category(key),
            page_size=10)
    raise tasklets.Return({
        'records': records,
        'pager': pager,
        'category': category
    })


@catalog.route('/')
@login_required
@render_to()
@context.toplevel
def filtered_records():
    categories = User2Category.get_for_user(user=g.user).map_async(
            lambda u2c: u2c.category)
    categories = yield categories
    if len(categories):
        records, pager = Record.paginate(Record.for_categories(categories))
        raise tasklets.Return({'records': records, 'pager': pager})
    raise tasklets.Return({})


@catalog.route('/mark')
@login_required
@context.toplevel
def mark_record():
    key_safe = request.args['key']
    if key_safe is None:
        raise tasklets.Return(jsonify({'status': 'error'}))
    response = {'status': 'success'}
    q = User2Record.relations(g.user, key_safe)
    record = yield q.get_async()
    if record is None:
        User2Record.create_async(g.user, key_safe)
        response.update({'data': 'created'})
    else:
        User2Record.delete(g.user, key_safe)
        response.update({'data': 'deleted'})
    raise tasklets.Return(jsonify(response))
