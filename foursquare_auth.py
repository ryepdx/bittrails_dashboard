import sqlite3 as db
from settings import FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET,FOURSQUARE_CALLBACK, DATABASE
from flask_oauth import OAuth
from flask import redirect, url_for, session, request, flash, Blueprint, current_app

foursquare_auth = Blueprint('foursquare_auth', __name__)

oauth = OAuth()

#foursquare = twitter_factory(oauth)
foursquare = oauth.remote_app('foursquare',
    base_url='https://api.foursquare.com/v2/',
    request_token_url = 'https://foursquare.com/oauth2/access_token',
    access_token_url ='https://foursquare.com/oauth2/access_token',
    authorize_url = 'https://foursquare.com/oauth2/authenticate',
    consumer_key = FOURSQUARE_CLIENT_ID, 
    consumer_secret = FOURSQUARE_CLIENT_SECRET
)

@foursquare_auth.route('/foursquare/login_fs')
def login_fs():
    url = url_for('.foursquare_authorized', next=request.args.get('home') or request.referrer or None)
    resp = foursquare.authorize( callback=url )
    return resp


@foursquare_auth.route('/foursquare/authorized')
@foursquare.authorized_handler
def foursquare_authorized(resp):
#   next_url = request.args.get('next') or url_for('.index')
    if resp is None:
#        flash(u'You denied the request to sign in.')
#        return redirect(next_url)
        return 'Did not authorize with fs.'
    

    session['foursquare_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['foursquare_user'] = resp['screen_name']
##    conn.commit()
##    conn.close()

    current_app.logger.info(resp)
    return redirect('/')
    flash('You were signed in as %s' % resp['screen_name'])
#    return redirect(next_url)


@foursquare_auth.route('/logout')
def logout():
    session.pop('foursquare_user')
    return redirect(request.args.get('next') or '/')

def logged_in():
    return 'foursquare_user' in session

@foursquare.tokengetter
def get_foursquare_oauth_token(maybe = None):
    #this thing with 'maybe' is a complete hack. I don't know why it is needed. -George
    if maybe: return session.get('foursquare_token')
    return session.get('oauth_token')
