from google.appengine.ext import blobstore

from flask import g, jsonify, request, redirect, url_for
from flaskext.babel import gettext as _

from ndb import context, tasklets

from auth.decorators import login_required

from core.decorators import render_to
from core.sitemap import sitemap
from . import catalog
from .forms import CategoryForm, RecordForm
from .models import Category, Record, User2Category, User2Record, Tag


@catalog.route('/cats/create', methods=['GET', 'POST'])
@login_required
@render_to()
def create_category():
    form = CategoryForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        form.save()
        return redirect(url_for('.list_categories'))
    return {'form': form}

sitemap.register('catalog.create_category', _('Create category'),
        child_of='catalog.list_categories')


@catalog.route('/cats')
@login_required
@render_to()
def list_categories():
    cats, pager = Category.paginate()
    return {'pager': pager, 'categories': cats}

sitemap.register('catalog.list_categories', _('Categories list'))


@catalog.route('/cats/<key>/records/create', methods=['GET'])
@catalog.route('/records/create', methods=['POST'])
@login_required
@render_to()
def create_record(key=None):
    sitemap.register('catalog.create_record', _('Create position'),
            child_of='catalog.list_records', args={'key': key})
    upload_url = blobstore.create_upload_url(url_for('.create_record'))
    form = RecordForm(len(request.form) and request.form or None,
            category=key)
    if request.method == 'POST' and form.validate():
        file_info = len(request.files) and request.files['attachment'] or None
        if file_info is not None:
            file_info = file_info.mimetype_params['blob-key']
        form.save(file_info)
        return redirect(url_for('.list_records', key=form.category.data))
    else:
        category = Category.get(key)
        return {'form': form,
                'category': category,
                'upload_url': upload_url}


@catalog.route('/cats/<key>/records')
@login_required
@render_to()
@context.toplevel
def list_records(key):
    sitemap.register('catalog.list_records', _('List positions'),
            child_of='catalog.list_categories', args={'key': key})
    category = yield Category.get_async(key)
    records, pager = Record.paginate(Record.for_category(key),
            page_size=10)
    raise tasklets.Return({
        'records': records,
        'pager': pager,
        'category': category
    })


@catalog.route('/records')
@login_required
@render_to()
@context.toplevel
def filtered_records():
    categories = User2Category.get_for_user(user=g.user).map_async(
            lambda u2c: u2c.category)
    count = yield User2Record.relations(g.user).count_async(1)
    categories = yield categories
    tags, pager = Tag.paginate()
    response = {'count': count, 'tags': tags}
    if len(categories):
        records, pager = Record.paginate(Record.for_categories(categories))
        response.update({'records': records, 'pager': pager})
    raise tasklets.Return(response)


sitemap.register('catalog.filtered_records', _('Positions'))


@catalog.route('/records/selected')
@login_required
@render_to()
def selected_records():
    relations = User2Record.relations(g.user)
    relations, pager = User2Record.paginate(relations)
    records = map(lambda rel: rel.record.get(), relations)
    return {'records': records, 'pager': pager}


sitemap.register('catalog.selected_records', _('Selected'),
        child_of='catalog.filtered_records')


@catalog.route('/records/mark')
@login_required
@context.toplevel
def mark_record():
    key_safe = request.args['key']
    if key_safe is None:
        raise tasklets.Return(jsonify({'status': 'error'}))
    response = {'status': 'success'}
    record_q = User2Record.relations(g.user, key_safe)
    record = yield record_q.get_async()
    if record is None:
        record_key = yield User2Record.create_async(g.user, key_safe)
        response.update({
            'data': {
                'action': 'created',
                'record': record_key.urlsafe()
             }})
    else:
        User2Record.delete(g.user, key_safe)
        response.update({'data': {'action': 'deleted'}})
    count_q = User2Record.relations(g.user)
    count = yield count_q.count_async(1)
    response['data'].update({'count': count})
    raise tasklets.Return(jsonify(response))


@catalog.route('/tags/<tag>')
@login_required
@render_to('catalog/filtered_records.html')
@context.toplevel
def tagged_records(tag):
    sitemap.register('catalog.tagged_records', _('With tag "%(tag)s"',
        tag=tag), child_of='catalog.filtered_records', args={'tag': tag})
    categories = User2Category.get_for_user(user=g.user).map_async(
            lambda u2c: u2c.category)
    categories = yield categories
    records = Record.for_categories(categories).filter(Record.tags.value
            == tag)
    tags, pager = Tag.paginate()
    records, pager = Record.paginate(records)
    raise tasklets.Return({
        'tags': tags,
        'records': records,
        'pager': pager,
        'page_title': _("Records for tag: %(tag)s", tag=tag)})
