from blinker import Namespace
import auth
from flask import url_for, session
from flask_mail import Message
from flask_login import login_user
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
        users = User.get_collection()
        twitter_handle = response.content['screen_name']
        user = users.find_one({'twitter_handle': twitter_handle})
        
        if user:
            user = User(**user)
        else:
            user = User(twitter_handle, session[TOKENS_KEY], confirmed = True)
            user_id = User.get_collection().insert(dict(user))
            user._id = user_id
            
        login_user(user)

def load_user(user_id):
    return User(**(User.get_collection().find_one(ObjectId(user_id))))

def connect_signals(app):
    signals = Namespace()
    #user_registered = signals.signal('register.user_registered')
    #user_registered.connect(send_confirmation_email)

    auth.signals.oauth_completed.connect(register_twitter_user)
    app.login_manager.user_loader(load_user)
