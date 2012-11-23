from flask import Flask, session
from settings import PORT, DEBUG, APP_SECRET_KEY
from auth import register_auth_blueprints

import home.views
import twitter_demo.views
import api.views

def main():
    app = Flask(__name__)
    app.secret_key = APP_SECRET_KEY
    register_auth_blueprints(app)
    app.register_blueprint(home.views.app)
    app.register_blueprint(twitter_demo.views.app, url_prefix = '/twitter_demo')
    app.register_blueprint(api.views.app, url_prefix = '/api')
    
    app.run(host = '0.0.0.0', port = PORT, debug = DEBUG)
        
if __name__ == '__main__':
    main()
