import sqlite3 as db
from fitbit import FitBit
from flask import Flask, request, session, url_for, redirect, render_template
from settings import DEBUG, APP_SECRET_KEY, DATABASE, FITBIT_ACCESS_TOKEN, TWITTER_USERNAME
from twitter_auth import twitter_auth

app = Flask(__name__)
app.register_blueprint(twitter_auth)
app.secret_key = APP_SECRET_KEY

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/oauth')
def oauth():
    api = FitBit()
    auth_url, auth_token = api.GetRequestToken()
    session['auth_token'] = auth_token
    return redirect(auth_url)

@app.route('/callback', methods=['POST', 'GET'])
def oauth_callback():
    api = FitBit()
    access_token = api.GetAccessToken(request.args.get('oauth_verifier'),
            session['auth_token'])
    conn = db.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""select fitbit_auth from users where username = ?  
            and fitbit_auth = ''""", (session['twitter_user'],))

    # Should change the database constraints to enforce uniqueness on
    # the username so I can change the below line to cur.rowcount == 1.
    if cur.rowcount > 0:
        cur.execute("""update users set fitbit_auth = ?
            where username = ?""", (access_token, session['twitter_user']))

    session['fitbit_access_token'] = access_token
    return 'Winning.'

@app.route('/login_stub')
def login_stub():
    session['fitbit_access_token'] = FITBIT_ACCESS_TOKEN
    session['twitter_user'] = TWITTER_USERNAME
    return 'Logged in.'

@app.route('/fitbit_steps')
def login_stub():
    api = FitBit()
    return api.ApiCall(session['fitbit_access_token'], apiCall='/1/user/-/activities/log/steps/date/today/7d.json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)


