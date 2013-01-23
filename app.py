from flask import Flask, session, redirect
from flask.ext.login import LoginManager
from settings import PORT, DEBUG, APP_SECRET_KEY
from errors import register_error_pages

import auth
import login
import home.views
import charts.views
import insights.views
import twitter_demo.views

def main():
    app = Flask('bittrails')
    app.secret_key = APP_SECRET_KEY
    app.config['TRAP_BAD_REQUEST_ERRORS'] = DEBUG
    
    register_error_pages(app)
    auth.register_auth_blueprint(app)
    app.register_blueprint(home.views.app)
    app.register_blueprint(charts.views.app, url_prefix='/charts')
    app.register_blueprint(insights.views.app, url_prefix='/insights')
    
    # Set up login and registration.
    login_manager = LoginManager()
    login_manager.setup_app(app)
    app.login_manager.user_loader(login.load_user)  
    
    if DEBUG:    
        @app.route('/url_map')
        def url_map():
            return str(app.url_map)
        
    # Run the app!
    app.run(host = '0.0.0.0', port = PORT, debug = DEBUG)

if __name__ == '__main__':
    main()
