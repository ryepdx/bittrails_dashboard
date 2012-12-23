from blinker import Namespace
import auth
from flask import url_for, session
from flask.ext.login import login_user, current_user
from login.models import User
from bson.objectid import ObjectId
from auth.signals import oauth_completed
from auth.auth_settings import TOKENS_KEY

def update_user(sender, response, access_token):
    if current_user.is_authenticated():
        session[TOKENS_KEY][sender.name] = access_token
        current_user.access_keys = session[TOKENS_KEY]
        User.get_collection().update(
            {'_id':current_user._id},
            {'$set': {'access_keys': current_user.access_keys}})
    else:
        login_user(register_user(response, access_token))
        

def register_user(response, access_token):
    btid = response.content.get('btid')
    
    if btid:
        users = User.get_collection()
        user = Users.find_one({'btid': btid})
        
        if user:
            user['access_key'] = access_token
            user['uids'][response.content['service']] = response.content['uid']
            user = User(**user)
            User.save(user)
        else:
            user = User(btid, access_token,
                uids = {response.content['service']: response.content['uid']}, 
                confirmed = True)
                 
            user_id = User.get_collection().insert(dict(user))
            user._id = user_id
        
        session[TOKENS_KEY] = user['access_key']
        
        return user
    return None

def load_user(user_id):
    return User(**(User.get_collection().find_one(ObjectId(user_id))))

def connect_signals(app):
    signals = Namespace()
    auth.signals.oauth_completed.connect(update_user)
    app.login_manager.user_(load_user)
