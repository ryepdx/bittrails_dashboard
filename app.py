from flask import Flask, session
from settings import PORT, DEBUG, APP_SECRET_KEY
from auth import register_auth_blueprints

import home.views
import twitter_demo.views

def oauth_completed(sender, response):
    session['%s_token' % sender.name] = sender.access_token

def main():
    app = Flask(__name__)
    app.secret_key = APP_SECRET_KEY
    app.register_blueprint(home.views.app)
    app.register_blueprint(twitter_demo.views.app, url_prefix = '/twitter_demo')
    oauth_services = register_auth_blueprints(app)
    
    # Connect the OAuth signal handlers.
    for service in oauth_services:
        oauth_services[service].oauth_completed.connect(
            oauth_completed, sender = oauth_services[service])
    
    app.run(host = '0.0.0.0', port = PORT, debug = DEBUG)
        
if __name__ == '__main__':
    main()
