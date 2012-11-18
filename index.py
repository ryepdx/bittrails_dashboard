import sqlite3 as db
from flask import Flask, session, url_for, redirect, render_template
from settings import DEBUG, APP_SECRET_KEY, DATABASE, \
                     FITBIT_ACCESS_TOKEN, TWITTER_USERNAME, FOURSQUARE_CLIENT_SECRET, FOURSQUARE_CALLBACK, FOURSQUARE_CLIENT_ID
TWITTER_REQUEST = "https://api.twitter.com/1.1/statuses/user_timeline.json"
from twitter_auth import twitter_auth, twitter
import requests

app = Flask(__name__)
app.register_blueprint(twitter_auth)
app.secret_key = APP_SECRET_KEY

@app.route('/')
def hello_world():
    if 'twitter_user' in session:
        data = {"screen_name" : session['twitter_user'],
                "count" : "20"}
        a = twitter.get(TWITTER_REQUEST,
                        data = data,
                        token = session.get('twitter_token'))
        session['tweets'] = a.data
        #uncomment to see print.html in action
        #session['test_dict'] = a.data[0]
        #return render_template('print.html')
        
    return render_template('index.html')

##@app.route('/oauth')
##def oauth():
##    return redirect('/')
##
##@app.route('/callback', methods=['POST', 'GET'])
##def oauth_callback():
##    return redirect('/')

@app.route('/login_stub')
def login_stub():
    session['fitbit_access_token'] = FITBIT_ACCESS_TOKEN
    session['twitter_user'] = TWITTER_USERNAME
    return 'Logged in.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=DEBUG)


