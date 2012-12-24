from flask_rauth import session
from flask import render_template, Blueprint, url_for, redirect
from flask.ext.login import logout_user, current_user
from settings_local import BITTRAILS_AUTH_URL
from auth import signals, API, BLUEPRINT
from auth.auth_settings import TOKENS_KEY

app = Blueprint('home', __name__, template_folder='templates')

@app.route('/')
def index():
    if current_user.is_authenticated():
        return redirect(url_for('.home'))
    else:
        return render_template('%s/index.html' % app.name,
            twitter_url = '/auth/twitter/begin')

@app.route('/login')
def login():
    return index()

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('.index'))

@app.route('/home')
def home():
    connected = []
    not_connected = []
    services = current_user['uids'].keys()
    
    for service in BLUEPRINT.realms:
        if service in services:
            connected.append(service)
        else:
            not_connected.append(service)
    
    show_tooltip = (len(connected) < 2)
    
    if 'twitter' in connected:
        tweets = API.get(
            ('twitter/statuses/user_timeline.json?screen_name=%s&count=%s'
                % (current_user.uids['twitter'], 6)), user = current_user).content
    else:
        tweets = None
        
    if 'foursquare' in connected:
        checkins = API.get(
            'foursquare/users/self/checkins?limit=2', user = current_user)
        
        if checkins and checkins.status == 200:
            checkins = checkins.content['response']['checkins']['items']
        else:
            checkins = []
    else:
        checkins = None
    
    return render_template('%s/home.html' % app.name,
        show_tooltip = show_tooltip,
        connected = connected,
        not_connected = not_connected,
        tweets = tweets,
        checkins = checkins)
    
@app.route('/insights')
def insights():
    pass

def create_api_test(apis):
    @app.route('/test')
    def test():
        return str(apis['bittrails'].get(
            'protected', oauth_token=session[TOKENS_KEY]['bittrails']).response.content)
            
    @app.route('/test_realm')
    def test():
        return str(apis['bittrails'].get(
            'protected_realm', oauth_token=session[TOKENS_KEY]['bittrails']).response.content)
