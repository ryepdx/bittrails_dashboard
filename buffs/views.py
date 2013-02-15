import iso8601
import pymongo
import itertools
import json
import bson
import datetime
import charts.utils
import buffs.utils
import collections
from flask import render_template, Blueprint, url_for, redirect, request
from flask.ext.login import current_user
from auth import API, BLUEPRINT
from buffs.models import BuffTemplate, CorrelationBuff
from settings import SERVER_TIMEZONE

app = Blueprint('buffs', __name__, template_folder='/templates')

@app.route('/')
def index():
    buffs_data = []
    intervals = ['day']
    aspects = {'lastfm': ['song_energy_average', 'scrobble_count']}
    colors = itertools.cycle(['steelblue', 'tomato'])
    thirty_days_ago = (
        datetime.datetime.now(SERVER_TIMEZONE).replace(hour = 0, minute = 0,
        second = 0, microsecond = 0) - datetime.timedelta(days = 30))
    
    # Grab the last buff we logged.
    last_buff = CorrelationBuff.find_one(None, sort = [('start', pymongo.DESCENDING)])
    if last_buff:
        start_date = max(thirty_days_ago,
            (iso8601.parse_date(last_buff['start'])
             + datetime.timedelta(days = 1)))
    else:
        start_date = thirty_days_ago
        
    # Just grabbing the correlations for this user from the last 30 days
    # or since the last logged buff, whichever is later.
    correlations = API.get_correlations(current_user, intervals, start_date,
        aspects)
    
    # Grab any correlations the user has yet to accept or decline.
    outstanding_correlations = [
        correlation for correlation in CorrelationBuff.find(
        { 'state': CorrelationBuff.OUTSTANDING })]
        
    # Cache all the new correlations.
    for interval in intervals:
        for correlation in correlations[interval]:
            buff = CorrelationBuff(user_id = current_user['_id'], **correlation)
            buff_id = CorrelationBuff.save(buff)
            correlation['_id'] = buff_id
    
    # Add all the outstanding correlations.
    for correlation in outstanding_correlations:
        if correlation['interval'] not in correlations:
            correlations[correlation['interval']] = []
        correlations[correlation['interval']].append(correlation)
    
    # Format the correlations as buffs.
    chart_index = 0
    for interval in intervals:
        for correlation in correlations[interval]:           
            
            template = buffs.utils.get_template_for(correlation)
            chart_data = [{
                'name': key.replace(
                    '_', ' ').title() + " " + aspect.replace('_', ' '),
                'color': colors.next(),
                'data': charts.utils.format_chart_data(API.get_chart_data(
                            current_user, key, aspect, interval,
                            start = correlation['start'],
                            end = correlation['end']))
                } for key, aspect_list in correlation['aspects'].items(
                    ) for aspect in aspect_list]
                            
            chart_data = charts.utils.normalize_chart_series(chart_data)
            
            buffs_data.append(
                {'text': template.render_using(correlation),
                 'chart_data': chart_data,
                 'chart_id': 'chart' + str(chart_index),
                 'buff_id': correlation['_id']
                })
            chart_index += 1
    
    return render_template('%s/index.html' % app.name, buffs = buffs_data)

@app.route('/<buff_id>')
def buff(buff_id):
    state_dict = {'accepted': CorrelationBuff.ACCEPTED,
                  'declined': CorrelationBuff.DECLINED }
    buff = CorrelationBuff.find_one({'_id': bson.ObjectId(buff_id)})
    
    if (request.args.get('_method') == 'put'
    and state_dict.get(request.args.get('state'))):
        buff['state'] = state_dict.get(request.args.get('state'))
        CorrelationBuff.save(buff)
    
    #return json.dumps(collections.OrderedDict(
    #    'correlation': buff['correlation']
    #})
    return redirect('/buffs/')
