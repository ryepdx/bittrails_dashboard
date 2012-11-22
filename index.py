import sqlite3 as db
from flask import Flask, session, url_for, redirect, render_template, request
from oauth_services import register_oauth_services
from settings import DEBUG, APP_SECRET_KEY, DATABASE, FITBIT_ACCESS_TOKEN, \
                     TWITTER_USERNAME
from settings_local import PORT, DEBUG
from collections import OrderedDict
import home.views

import requests, re

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

def oauth_completed(sender, response):
    session['%s_token' % sender.name] = sender.access_token

def main():
    app.register_blueprint(home.views.app)
    oauth_services = register_oauth_services(app)
    
    # Connect the OAuth signal handlers.
    for service in oauth_services:
        oauth_services[service].oauth_completed.connect(
            oauth_completed, sender = oauth_services[service])
    
    app.run(host = '0.0.0.0', port = PORT, debug = DEBUG)
        
if __name__ == '__main__':
    main()
