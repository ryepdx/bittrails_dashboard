import sqlite3 as db
from flask import Flask, session, url_for, redirect, render_template, request
from settings import DEBUG, APP_SECRET_KEY, DATABASE, \
                     FITBIT_ACCESS_TOKEN, TWITTER_USERNAME, FOURSQUARE_CLIENT_SECRET, FOURSQUARE_CALLBACK, FOURSQUARE_CLIENT_ID
TWITTER_REQUEST = "https://api.twitter.com/1.1/statuses/user_timeline.json"
from twitter_auth import twitter_auth, twitter
from datetime import datetime
import requests, re

app = Flask(__name__)
app.register_blueprint(twitter_auth)
app.secret_key = APP_SECRET_KEY

## NOTA BENE:
## serving print.html is used to expose code like a print statement
##  if availuable, session['test_value'] will be printed
##  if availuable, each item in session['test_list'] will be printed
##      if session['test_list_key'] exists, item[session['test_list_key']]
##      will be printed in place of item
##  if availuable, each key/value pair in session['test_dict'] will be printed

def convert_twitter_time(time_string):
    a = re.search("\+[0-9]{4} ", time_string)
    time_string = time_string[:a.start()]+time_string[a.end():].strip()
    time = datetime.strptime(time_string, "%a %b %d %H:%M:%S %Y")
    return time.strftime("%Y-%m-%d %H:%M:%S")

def get_tweet_data(user, count):
    tweets = list()
    while (count > 0):
        #keep track of how many tweets to get
        get = 30
        if (count < 30):
            get = count
        count -= get
        data = {"screen_name" : user,
                "count" : str(get)}
        if len(tweets): #don't get the same tweets twice
            data["max_id"] = str(tweets[-1]['id']-1)
        resp = twitter.get(TWITTER_REQUEST,
                           data = data,
                           token = session.get('twitter_token'))
        
        for tweet_data in resp.data:
            tweet_slim = dict()
            tweet_slim['id'] = tweet_data['id']
            tweet_slim['timestamp'] = convert_twitter_time(tweet_data['created_at'])
            tweet_slim['text'] = tweet_data['text']
            tweets.append(tweet_slim)
    return tweets
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/twitter')
def twitter_demo():
    if 'twitter_user' in session:
        user = session['twitter_user']
        if 'user' in request.args:
            user = request.args['user']
        #user = "LucianNovo"
        session['user'] = user
        session['tweets'] = get_tweet_data(user, 200)
        #session['test_dict'] = request.args
        #session['test_list'] = session['tweets']
        #session['test_list_value_key'] = "timestamp"
        #return render_template('print.html')
        
    return render_template('twitter.html')

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

@app.route('/correlate')
def correlate():
    date_format = '%Y-%m-%d %H'
    datastreams = {}
    raw_streams = session.get('datastreams')
    
    streams = raw_streams.keys()
    max_date = None
    min_date = None
    hours = []

    for key in streams:
        stream = streams[key]
        first_date = datetime.strptime(stream[0], '%Y-%m-%d %H:%M:%S')
        last_date = datetime.strptime(stream[len(stream)], '%Y-%m-%d %H:%M:%S')
        
        if max_date < last_date or max_date == None:
            max_date = last_date
            
        if min_date > first_date or min_date == None:
            min_date = first_date
    
    counts_blank = {max_date.strftime(date_format): 0}
    while max_date > min_date:
        max_date = max_date - timedelta(hours=1)
        counts_blank[max_date.strftime(date_format)] = 0 
        
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=DEBUG)


