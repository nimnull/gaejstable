from flask import g, jsonify, request, redirect, url_for

from catalog.models import Category, User2Category
from core.decorators import render_to

from .. import auth
from ..decorators import login_required
from ..forms import ProfileForm


@auth.route('/profile')
@login_required
@render_to('auth/profile_view.html')
def view_profile():
    return {'user': g.user}


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


@auth.route('/profile/settings')
@login_required
@render_to('/auth/profile_setup.html')
def setup_profile():
    cats, pager = Category.paginate(page_size=40)
    return {'categories': cats, 'pager': pager}


@auth.route('/profile/toggle_cat', methods=['POST'])
@login_required
def toggle_category():
    resp = {'status': 'success'}
    urlkey = request.args.get('key')
    category = urlkey and Category.get_by_urlsafe(urlkey) or None
    user2category = category and User2Category.get(g.user, category) or None
    if user2category is not None:
        user2category.key.delete()
        resp.update({'data': 'deleted'})
    elif category is not None:
        User2Category.create(g.user, category)
        resp.update({'data': 'created'})
    else:
        resp['status'] = 'error'
    return request.is_xhr and jsonify(**resp) or redirect(url_for('.setup_profile'))
