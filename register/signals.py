from blinker import Namespace
from flask import url_for
from flaskext.mail import Message

signals = Namespace()
user_registered = signals.signal('register.user_registered')
user_registered.connect(send_confirmation_email)

def send_confirmation_email(user):
    """
    Send the awaiting for confirmation mail to the user.
    """
    subject = "We're waiting for your confirmation!!"
    mail_to_be_sent = Message(subject=subject, recipients=[user['email']])
    confirmation_url = url_for('.confirm', user_id=user['_id'],
        _external=True)
    mail_to_be_sent.body = "Dear %s, click here to confirm: %s" %
        (user['email'], confirmation_url)
    from mailer import mail
    mail.send(mail_to_be_sent)
