from threading import Thread
from flask import current_app, render_template
from flask_mail import Message

import app
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()

    email_list = to.split(',')

    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])

    for x in email_list:
        msg.add_recipient(x)

    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
