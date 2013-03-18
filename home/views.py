from flask_rauth import session
from flask import render_template, Blueprint, url_for, redirect
from flask.ext.login import logout_user, current_user
from settings import BITTRAILS_AUTH_URL, DEBUG
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
    
    return render_template('%s/home.html' % app.name,
        show_tooltip = show_tooltip,
        connected = connected,
        not_connected = not_connected,
        DEBUG = DEBUG)
    
def create_api_test(apis):
    @app.route('/test')
    def test():
        return str(apis['bittrails'].get(
            'protected', oauth_token=session[TOKENS_KEY]['bittrails']).response.content)
            
    @app.route('/test_realm')
    def test():
        return str(apis['bittrails'].get(
            'protected_realm', oauth_token=session[TOKENS_KEY]['bittrails']).response.content)
