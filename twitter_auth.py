import sqlite3 as db
from settings import TWITTER_KEY, TWITTER_SECRET, DATABASE
from flask_oauth import OAuth
from flask import redirect, url_for, session, request, flash, Blueprint, current_app

twitter_auth = Blueprint('twitter_auth', __name__)

oauth = OAuth()
#twitter = twitter_factory(oauth)
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=TWITTER_KEY,
    consumer_secret=TWITTER_SECRET
)

@twitter_auth.route('/login')
def login():
    url = url_for('.twitter_authorized', next=request.args.get('home') or request.referrer or None)
    resp = twitter.authorize( callback=url )
    return resp


@twitter_auth.route('/twitter/authorized')
@twitter.authorized_handler
def twitter_authorized(resp):
#    next_url = request.args.get('next') or url_for('.index')
    if resp is None:
#        flash(u'You denied the request to sign in.')
#        return redirect(next_url)
        return 'Did not authorize.'

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['twitter_user'] = resp['screen_name']

    return redirect('/')
#    flash('You were signed in as %s' % resp['screen_name'])
#    return redirect(next_url)


@twitter_auth.route('/logout')
def logout():
    session.pop('twitter_user')
    return redirect(request.args.get('next') or '/')

def logged_in():
    return 'twitter_user' in session

@twitter.tokengetter
def get_twitter_oauth_token():
        return session.get('oauth_token')
