import sqlite3 as db
from fitbit import FitBit
from flask import Flask, request, session, url_for, redirect, render_template
from settings import DEBUG, APP_SECRET_KEY, DATABASE
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
    cur.execute('select fitbit_auth from users where username = ? 
            and fitbit_auth = \'\'', (session['twitter_user'],))

    # Should change the database constraints to enforce uniqueness on
    # the username so I can change the below line to cur.rowcount == 1.
    if cur.rowcount > 0:
        cur.execute('update users set fitbit_auth = ?
            where username = ?', (access_token, session['twitter_user']))

    return 'Winning.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)


