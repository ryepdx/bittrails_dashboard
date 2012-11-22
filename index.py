import sqlite3 as db
from flask import Flask, session, url_for, redirect, render_template, request
from settings import DEBUG, APP_SECRET_KEY, DATABASE, FITBIT_ACCESS_TOKEN, \
                     TWITTER_USERNAME, FOURSQUARE_CLIENT_SECRET, \
                     FOURSQUARE_CALLBACK, FOURSQUARE_CLIENT_ID, \
                     TWITTER_KEY, TWITTER_SECRET, FOURSQUARE_CLIENT_ID, \
                     FOURSQUARE_CLIENT_SECRET
from settings_local import PORT, DEBUG
from collections import OrderedDict
from blinker import signal

TWITTER_REQUEST = "https://api.twitter.com/1.1/statuses/user_timeline.json"
from oauth_blueprint import OAuthBlueprint, OAuth2Blueprint
from datetime import datetime
import requests, re

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

## NOTE:
## serving print.html is used to expose code like a print statement
##  if availuable, session['test_value'] will be printed
##  if availuable, each item in session['test_list'] will be printed
##      if session['test_list_key'] exists, item[session['test_list_key']]
##      will be printed in place of item
##  if availuable, each key/value pair in session['test_dict'] will be printed

def twitter_oauth_completed(sender, response):
    session['twitter_token'] = sender.access_token
    session['twitter_user'] = response.content['screen_name'] 
    
def foursquare_oauth_completed(sender, response):
    session['foursquare_token'] = sender.access_token

def main():
    app.config.update(
        TWITTER_CONSUMER_KEY = TWITTER_KEY,
        TWITTER_CONSUMER_SECRET = TWITTER_SECRET
    )
    
    twitter = OAuthBlueprint(
        name = 'twitter',
        base_url = 'https://api.twitter.com/1/',
        request_token_url = 'https://api.twitter.com/oauth/request_token',
        access_token_url = 'https://api.twitter.com/oauth/access_token',
        authorize_url = 'https://api.twitter.com/oauth/authenticate',
        consumer_key = TWITTER_KEY,
        consumer_secret = TWITTER_SECRET,
        oauth_refused_view = 'index',
        oauth_completed_view = 'index'
    )
    
    foursquare = OAuth2Blueprint(
        name = 'foursquare',
        base_url = 'https://api.foursquare.com/v2/',
        access_token_url ='https://foursquare.com/oauth2/access_token',
        authorize_url = 'https://foursquare.com/oauth2/authenticate',
        consumer_key = FOURSQUARE_CLIENT_ID, 
        consumer_secret = FOURSQUARE_CLIENT_SECRET,
        oauth_refused_view = 'index',
        oauth_completed_view = 'index'
    )
    
    # Connect signal handlers to our OAuth handlers.
    # These will handle saving access tokens and setting session variables,
    # allowing us to our code nice and decoupled.
    twitter.oauth_completed.connect(twitter_oauth_completed, sender=twitter)
    foursquare.oauth_completed.connect(foursquare_oauth_completed, sender=foursquare)
    
    app.register_blueprint(twitter.blueprint, url_prefix='/twitter')
    app.register_blueprint(foursquare.blueprint, url_prefix='/foursquare')
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
    
def convert_twitter_time(time_string):
    a = re.search("\+[0-9]{4} ", time_string)
    time_string = time_string[:a.start()]+time_string[a.end():].strip()
    time = datetime.strptime(time_string, "%a %b %d %H:%M:%S %Y")
    return time.strftime("%Y-%m-%d %H:%M:%S")

def twitter_time_str_to_datetime(time_string):
    a = re.search("\+[0-9]{4} ", time_string)
    time_string = time_string[:a.start()]+time_string[a.end():].strip()
    return datetime.strptime(time_string, "%a %b %d %H:%M:%S %Y")

def format_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def suffix(i):
    if i < 12: return 'am'
    else: return 'pm'

def hour_str(i):
    return str((i-1)%12+1)+suffix(i)

def get_tweet_data(user, count):
    DATA_TO_KEEP = {'id' : 'id',
                    'timestamp' : 'created_at',
                    'text' : 'text'}
    tweets = list()
    userdata = None
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
        if not userdata:
            userdata = resp.data[0]['user']
        for tweet_data in resp.data:
            tweet_slim = dict()
            for key in DATA_TO_KEEP:
                tweet_slim[key] = tweet_data[DATA_TO_KEEP[key]]
            tweets.append(tweet_slim)
    return userdata, tweets

def calculate_per_day(tweets, offset):
    latest = twitter_time_str_to_datetime(tweets[0]['timestamp'])
    earliest = twitter_time_str_to_datetime(tweets[-1]['timestamp'])
    num_days = (latest-earliest).days
    if num_days == 0: num_days = 1
    day = dict()
    for i in range(24):
        day[i] = 0
    for tweet in tweets:
        dt = twitter_time_str_to_datetime(tweet['timestamp'])
        dt += timedelta(seconds = offset)
        day[dt.hour] += 1
    return OrderedDict([(hour_str(hour), 1.0*day[hour]) for hour in range(24)])
##    return [hour_str(i) for i in range(24)], \
##           [1.0*day[hour]/num_days for hour in day.keys()]

def clean_test_values():
    if 'test_value' in session: del session['test_value']
    if 'test_dict' in session: del session['test_dict']
    if 'test_list' in session: del session['test_list']
    if 'test_list_value_key' in session: del session['test_list_value_key']
 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/twitter_demo')
def twitter_demo():
    if 'twitter_user' in session:
        user = session['twitter_user']
        if 'user' in request.args:
            user = request.args['user']
        count = 300
        if 'count' in request.args:
            try:
                count = int(request.args['count'])
            finally:
                pass
        #user = "LucianNovo"
        session['user'] = user
        userdata, tweets = get_tweet_data(user, count)
        utc_offset = userdata['utc_offset']
        average_day = calculate_per_day(tweets, utc_offset)
        session['tweets'] = tweets
        session['average_per_day'] = average_day
        clean_test_values()
        #session['test_value'] = 
        #session['test_dict'] = average_day
        session['test_dict'] = average_day
        #session['test_list_value_key'] = 
        return render_template('print.html')
        
    return render_template('twitter.html')

@app.route('/foursquare_demo')
def foursquare_demo():
    if 'foursquare_user' in session:
        user = session['foursquare_user']
        if 'user' in request.args:
            user = request.args['user']
        #user = "LucianNovo"
        session['user'] = user
        session['tweets'] = get_tweet_data(user, 200)
        #session['test_dict'] = request.args
        #session['test_list'] = session['tweets']
        #session['test_list_value_key'] = "timestamp"
        #return render_template('print.html')
    return render_template('foursquare.html')

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
    main()

