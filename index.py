import sqlite3 as db
from flask import Flask, session, url_for, redirect, render_template
from settings import DEBUG, APP_SECRET_KEY, DATABASE, FITBIT_ACCESS_TOKEN, TWITTER_USERNAME
from twitter_auth import twitter_auth
import requests

app = Flask(__name__)
app.register_blueprint(twitter_auth)
app.secret_key = APP_SECRET_KEY
app.logger.log(0, "test")
@app.route('/')
def hello_world():
##    if 'twitter_user' in session:
##        a = requests.get("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="+"ryepdx")
##        app.logger.log(0, str(type(a)))
    return render_template('index.html')

@app.route('/login_stub')
def login_stub():
    session['fitbit_access_token'] = FITBIT_ACCESS_TOKEN
    session['twitter_user'] = TWITTER_USERNAME
    return 'Logged in.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=DEBUG)


