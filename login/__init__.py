from blinker import Namespace
import auth
from flask import url_for, session
from flask.ext.login import login_user, current_user
from login.models import User
from bson.objectid import ObjectId
from auth.signals import oauth_completed
from auth.auth_settings import TOKENS_KEY

def update_user(sender, request, access_token):
    if current_user.is_authenticated():
        session[TOKENS_KEY] = access_token
        current_user.access_key = access_token
        current_user.uids[request.args['service']] = request.args['uid']
        
        User.get_collection().update(
            {'_id':current_user._id},
            {'$set':
                {'access_key': current_user.access_key,
                 'uids': current_user.uids
                }
            })
    else:
        login_user(register_user(request, access_token))
        

def register_user(request, access_token):
    btid = request.args.get('btid')
    
    if btid:
        users = User.get_collection()
        user = User.find_one({'btid': btid})
        
        if user:
            user['access_key'] = access_token
            user['uids'][request.args['service']] = request.args['uid']
            User.save(user)
            user = User(**user)
        else:
            user = User(btid, access_token,
                uids = {request.args['service']: request.args['uid']}, 
                confirmed = True)
                 
            user_id = User.get_collection().insert(dict(user))
            user._id = user_id
        
        session[TOKENS_KEY] = user['access_key']
        
        return user
    return None

def load_user(user_id):
    return User(**(User.get_collection().find_one(ObjectId(user_id))))

auth.signals.oauth_completed.connect(update_user)
