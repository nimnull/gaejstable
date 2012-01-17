import logging
from flask import render_template
from google.appengine.api import app_identity, mail

from settings import SITE_TITLE


def send(rcpt, subject, template, context):
    app_id = app_identity.get_application_id()
    email = {
        'sender': "Mail robot on {} <no-reply@{}.appspotmail.com>".format(SITE_TITLE,
                app_id),
        'to': rcpt,
        'subject': subject,
        'body': render_template(template, **context)
    }
    logging.info(email)
    mail.send_mail(**email)
