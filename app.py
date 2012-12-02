from flask import Flask, session, redirect
from flask.ext.login import LoginManager
from settings import PORT, DEBUG, APP_SECRET_KEY
from errors import register_error_pages

import home.views
import twitter_demo.views

def main():
    app = Flask(__name__)
    app.secret_key = APP_SECRET_KEY
    
    register_error_pages(app)
    app.register_blueprint(home.views.app)
    
    # Set up login and registration.
    #login_manager = LoginManager()
    #login_manager.setup_app(app)
    
    # Run the app!
    app.run(host = '0.0.0.0', port = PORT, debug = DEBUG)

if __name__ == '__main__':
    main()
