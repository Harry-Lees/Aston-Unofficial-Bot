from flask import url_for
from flask_mail import Message
from app.extensions import mail

def send_email(app, to, subject, template):
    msg = Message(
        subject,
        recipients = [to],
        html = template,
        sender = app.config['MAIL_DEFAULT_SENDER']
    )

    mail.send(msg)