import datetime
from flask import render_template, Blueprint, url_for, redirect
from flask.ext.login import current_user
from auth import API, BLUEPRINT

app = Blueprint('buffs', __name__, template_folder='/templates')

@app.route('/')
def index():
    # Just grabbing the correlations for this user from the last 30 days.
    correlations = API.get_correlations(current_user, ['day'],
        (datetime.datetime.utcnow() - datetime.timedelta(days = 30)),
        {'lastfm': ['song_energy_average', 'scrobble_count']})
    
    return render_template(
        '%s/index.html' % app.name, correlations = correlations)
