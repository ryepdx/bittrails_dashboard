from flask_rauth import session
from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask.ext.login import logout_user, current_user, login_required
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
            
    connected += [
        stream[0] for stream in API.get_custom_datastreams(current_user)]
    
    show_tooltip = (len(connected) < 2)
    
    return render_template('%s/home.html' % app.name,
        show_tooltip = show_tooltip,
        connected = connected,
        not_connected = not_connected,
        DEBUG = DEBUG)

@app.route('/custom_datastream', methods=['GET'])
@login_required
def custom_datastream_form():
    return render_template('%s/custom_datastream.html' % app.name)

@app.route('/custom_datastream', methods=['POST'])
@login_required
def create_custom_datastream():
    API.create_custom_datastream(current_user,
        request.form.get('url'), request.form.get('name'))
    flash("Custom datastream created!")
    return redirect(url_for('.home'))

def create_api_test(apis):
    @app.route('/test')
    def test():
        return str(apis['bittrails'].get(
            'protected', oauth_token=session[TOKENS_KEY]['bittrails']).response.content)
            
    @app.route('/test_realm')
    def test():
        return str(apis['bittrails'].get(
            'protected_realm', oauth_token=session[TOKENS_KEY]['bittrails']
        ).response.content)
