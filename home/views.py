from flask_rauth import session
from flask import render_template, Blueprint, url_for, redirect
from flask.ext.login import logout_user, current_user
from auth.decorators import APIs_route
from settings_local import BITTRAILS_AUTH_URL
from auth import signals
from auth.auth_settings import TOKENS_KEY

app = Blueprint('home', __name__, template_folder='templates')

@app.route('/')
def index():
    #if current_user.is_authenticated():
    #    return redirect(url_for('.home'))
    #else:
    # TODO: Add back in a user concept.
    return render_template('%s/index.html' % app.name,
            twitter_url = '%s/twitter/begin' % 
                BITTRAILS_AUTH_URL)

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('.index'))

@APIs_route(app, '/home')
def home(apis):
    services = apis.keys()
    connected = []
    not_connected = []
    
    for service in services:
        if service in current_user.access_keys:
            connected.append(service)
        else:
            not_connected.append(service)
    
    show_tooltip = (len(connected) < 2)
    
    if 'twitter' in connected:
        tweets = apis['twitter'].get(
            ('statuses/user_timeline.json?screen_name=%s&count=%s'
                % (current_user.twitter_handle, 6))).content
    else:
        tweets = None
        
    if 'foursquare' in connected:
        checkins = apis['foursquare'].get(
            'users/self/checkins?limit=2', user = current_user).content
        checkins = checkins['response']['checkins']['items']
    else:
        checkins = None
    
    return render_template('%s/home.html' % app.name,
        show_tooltip = show_tooltip,
        connected = connected,
        not_connected = not_connected,
        tweets = tweets,
        checkins = checkins)


def create_api_test(apis):
    @app.route('/test')
    def test():
        return str(apis['bittrails'].get(
            'protected', oauth_token=session[TOKENS_KEY]['bittrails']).response.content)
            
    @app.route('/test_realm')
    def test():
        return str(apis['bittrails'].get(
            'protected_realm', oauth_token=session[TOKENS_KEY]['bittrails']).response.content)
