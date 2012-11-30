from blinker import Namespace
import auth
from flask import url_for, session
from flask_mail import Message
from flask_login import login_user
from app import login_manager
from register.models import User
from bson.objectid import ObjectId
from auth.signals import oauth_completed
from auth.auth_settings import TOKENS_KEY

def send_confirmation_email(user):
    """
    Send the awaiting for confirmation mail to the user.
    """
    from app import mail
    
    subject = "We're waiting for your confirmation!!"
    mail_to_be_sent = Message(subject=subject, recipients=[user['email']])
    confirmation_url = url_for('.confirm', user_id=user['_id'],
        _external=True)
    mail_to_be_sent.body = ("Dear %s, click here to confirm: %s" %
        (user['email'], confirmation_url))
    
    mail.send(mail_to_be_sent)

def register_twitter_user(sender, response, access_token):
    if sender.name == 'twitter' and 'screen_name' in response.content:
        user = User(response.content['screen_name'], session[TOKENS_KEY], confirmed = True)
        user_id = User.get_collection().insert(dict(user))
        user._id = user_id
        login_user(user)

@login_manager.user_loader
def load_user(user_id):
    return User(User.get_collection().find_one(ObjectId(user_id)))


def connect_signals():
    signals = Namespace()
    #user_registered = signals.signal('register.user_registered')
    #user_registered.connect(send_confirmation_email)

    auth.signals.oauth_completed.connect(register_twitter_user)
