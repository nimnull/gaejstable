from flask import g, request, redirect, url_for

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
@render_to()
def profile_settings():
    return {}
