from flask import g, jsonify, request, redirect, url_for
from flaskext.babel import gettext as _
from ndb import context, tasklets

from catalog.models import Category, User2Category
from core.decorators import render_to
from core.sitemap import sitemap

from .. import auth
from ..decorators import login_required
from ..forms import ProfileForm


@auth.route('/profile')
@login_required
@render_to('auth/profile_view.html')
def view_profile():
    return {'user': g.user}


sitemap.register('auth.profile', _('Profile'))


@auth.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@render_to('auth/profile_edit.html')
def edit_profile():
    form = ProfileForm(len(request.form) and request.form or None, obj=g.user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(g.user)
        g.user.put()
        return redirect(url_for('.view_profile'))
    return {'user': g.user, 'form': form}


sitemap.register('auth.edit_profile', _('Edit'), child_of='auth.profile')


@auth.route('/profile/settings')
@login_required
@render_to('/auth/profile_setup.html')
def setup_profile():
    cats, pager = Category.paginate(page_size=40)
    return {'categories': cats, 'pager': pager}


sitemap.register('auth.setup_profile', _('Settings'), child_of='auth.profile')


@auth.route('/profile/toggle_cat', methods=['POST'])
@login_required
@context.toplevel
def toggle_category():
    resp = {'status': 'success'}
    urlkey = request.args.get('key')
    if urlkey is None:
        raise tasklets.Return({'status': 'error'})
    category = yield Category.get_async(urlkey)
    u2c = yield User2Category.delete_async(g.user, category)
    if u2c:
        resp.update({'data': 'deleted'})
    elif category is not None:
        User2Category.create_async(g.user, category)
        resp.update({'data': 'created'})
    else:
        resp['status'] = 'error'
    raise tasklets.Return(request.is_xhr and jsonify(**resp) or
            redirect(url_for('.setup_profile')))
