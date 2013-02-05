import itertools
import json
import datetime
import charts.utils
import buffs.utils
from flask import render_template, Blueprint, url_for, redirect
from flask.ext.login import current_user
from auth import API, BLUEPRINT
from buffs.models import BuffTemplate

app = Blueprint('buffs', __name__, template_folder='/templates')

@app.route('/')
def index():
    buff_text = []
    intervals = ['day']
    aspects = {'lastfm': ['song_energy_average', 'scrobble_count']}
    colors = itertools.cycle(['steelblue', 'tomato'])
    
    # Just grabbing the correlations for this user from the last 30 days.
    correlations = API.get_correlations(current_user, intervals,
        (datetime.datetime.utcnow() - datetime.timedelta(days = 30)),
        aspects)
        
    i = 0
    series = [{
        'name': key.replace('_', ' ').title() + " " + aspect.replace('_', ' '),
        'color': colors.next(),
        'data': charts.utils.format_chart_data(API.get_chart_data(
                current_user, key, aspect, 'day'
            ))
        } for key, aspect_list in aspects.items() for aspect in aspect_list]
    
    series = charts.utils.normalize_chart_series(series)
    
    for interval in intervals:
        for correlation in correlations[interval]:
            template = buffs.utils.get_template_for(correlation)
            buff_text.append(template.render_using(correlation))
    
    return render_template('%s/index.html' % app.name,
        buff_text = buff_text, series = series)
