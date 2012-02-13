import uuid
from flask import flash, g, request, redirect, session, url_for
from flaskext.babel import gettext as _

from google.appengine.api import app_identity

from settings import SITE_TITLE

from core.decorators import render_to
from core.sitemap import sitemap
from core import email

from .. import auth
from ..decorators import login_required
from ..forms import (SignUpForm, SignInForm, AskRecoverForm,
    PasswordResetForm)
from ..models import User
from ..utils import login, logout


HOSTNAME = app_identity.get_default_version_hostname()


@auth.route('/sign_up', methods=['GET', 'POST'])
@render_to()
def sign_up():
    key = request.args.get('key')
    if g.user is not None:
        return redirect(url_for('core.index'))
    elif key is not None and session.pop('uuid', None) == key:
        return {'finished': True}

    form = SignUpForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        user = form.save()
        session['uuid'] = str(uuid.uuid1())
        email.send(rcpt=user.username,
            subject=_("[%s] Account activation" % SITE_TITLE),
            template='auth/email/activate.html',
            context={'user': user, 'hostname': HOSTNAME})
        return redirect(url_for('.sign_up', key=session['uuid']))
    return {'form': form}


sitemap.register('auth.sign_up', _('Sign Up'))


@auth.route('/sign_up/activate')
@render_to()
def activate():
    token = request.args.get('token')
    user = User.validate_token(token)
    if token is not None and user:
        user.is_active = True
        login(user)
        return redirect(url_for('.view_profile'))
    return {}


sitemap.register('auth.activate', _('Activate account'),
        child_of='auth.sign_up')


@auth.route('/sign_in', methods=['GET', 'POST'])
@render_to()
def sign_in():
    if request.args.get('next'):
        session['next'] = request.args['next']
    form = SignInForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        user = User.check_password(**form.data)
        if user and user.is_active:
            login(user)
            next_url = session.pop('next', None) or url_for('core.index')
            return redirect(next_url)
        elif user and not user.is_active:
            flash(_('Please activate your account first'),
                        category='warning')
        else:
            flash(_('There is no user with provided email or password'),
                        category='warning')
            return redirect(url_for('.sign_in'))
    return {'form': form}


sitemap.register('auth.sign_in', _('Sign In'))


@auth.route('/sign_out')
@login_required
@render_to()
def sign_out():
    logout()
    return redirect(url_for('core.index'))


@auth.route('/recover', methods=['GET', 'POST'])
@render_to('auth/recover_ask.html')
def ask_recovery():
    form = AskRecoverForm(len(request.form) and request.form or None)
    if request.method == 'POST' and form.validate():
        user = form.get_user()
        email.send(rcpt=user.username,
            subject=_("[%(title)s] Password recovery", title=SITE_TITLE),
            template='auth/email/recovery.html',
            context={'user': user, 'hostname': HOSTNAME}
        )
        flash(_("We've just sent an email to <strong>%(username)s</strong> with "
                "the special link for you to reset lost password.",
                username=user.username), category='success')
        session['recover_sent'] = True
        return redirect(url_for('.ask_recovery'))
    return {'form': form, }


sitemap.register('auth.ask_recovery', _('Recover lost password'))


@auth.route('/recover/finish', methods=['GET', 'POST'])
@render_to('auth/recover_finish.html')
def finish_recovery():
    token = request.args.get('token')
    form = PasswordResetForm(len(request.form) and request.form or
            request.args)
    if token is not None and User.validate_token(token):
        return {'form': form}
    elif request.method == 'POST' and form.validate():
        session.pop('recover_sent', None)
        user = form.save()
        user.is_active = True
        login(user)
        return redirect(url_for('.view_profile'))
    flash(_('Your didn\'t provide a token or it is no longer valid. <a '
            'href="%(url)s">Request password recovery</a> again please.',
            url=url_for('.ask_recovery')), category='warning')
    return {}


sitemap.register('auth.finish_recovery', _('Reset password'))
