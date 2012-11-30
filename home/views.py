from flask import render_template, Blueprint, url_for, session, redirect
from flask.ext.login import logout_user, current_user

app = Blueprint('home', __name__, template_folder='templates')

@app.route('/')
def index():
    if current_user.is_authenticated():
        return redirect(url_for('.home'))
    else:
        return render_template('%s/index.html' % app.name,
            twitter_url = '/auth/twitter/begin')

@app.route('/clear_session')
def clear_session():
    logout_user()
    session.clear()
    return redirect(url_for('.index'))
        
@app.route('/home')
def home():
    return render_template('%s/home.html' % app.name)

