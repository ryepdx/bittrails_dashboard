import iso8601
import pymongo
import itertools
import json
import bson
import datetime
import time
import charts.utils
import buffs.utils
import collections
from flask import render_template, Blueprint, url_for, redirect, request
from flask.ext.login import current_user
from auth import API, BLUEPRINT
from buffs.models import BuffTemplate, CorrelationBuff
from buffs.helper_classes import CorrelationBuffCharts
from settings import SERVER_TIMEZONE

app = Blueprint('buffs', __name__, template_folder='/templates')

@app.route('/')
def index():
    active_buffs = []
    accepted_buffs = []
    outstanding_buffs = []
    paths = ['lastfm/scrobbles/echonest/totals',
             'lastfm/scrobbles/echonest/energy/averages']
    group_by_intervals = {
        "day": ["year","month","day"]#, "week": ["isoyear", "isoweek"],
        #"month": ["year", "month"], "year": ["year"]
    }
    continuous = True
    
    today = datetime.datetime.now(SERVER_TIMEZONE).replace(
        hour = 0, minute = 0, second = 0, microsecond = 0)
    a_year_ago = (today - datetime.timedelta(days = 365))
    
    # Grab the last buff we logged.
    # TODO: Make this more robust. Should really be grabbing the latest 'end'
    # date where 'end' is not null. But sorting by 'end' seems to be producing
    # strange results.
    last_buff = CorrelationBuff.find_one(None, sort = [('_id', pymongo.DESCENDING)])
    if last_buff:
        start_date = max(a_year_ago, (datetime.datetime(
            *(last_buff['end'] if last_buff['end'] else last_buff['start']))
            + datetime.timedelta(days = 1)).replace(tzinfo = SERVER_TIMEZONE))
    else:
        start_date = a_year_ago
    
    # Grab any correlations the user has yet to accept or decline.
    outstanding_buffs = CorrelationBuff.find_outstanding(lazy = False)
    
    for interval, group_by in group_by_intervals.items():
        intervalString = ",".join(sorted(group_by))
        
        # Just grabbing the correlations for this user from the last 30 days
        # or since the last logged buff, whichever is later.
        new_correlations = API.get_correlations(
            current_user, paths, group_by, start_date, continuous = True)
        
        # Cache all the new correlations.
        # TODO: Filter out any that were previously saved as active buffs and
        # update their end values if applicable.
        for correlation in new_correlations:
            buff = CorrelationBuff(user_id = current_user['_id'], **correlation)
            end = dict(zip(correlation['group_by'], correlation['end']))
            end = datetime.datetime(end['year'], end['month'], end['day'])
            
            # If the correlation end date is today, then we consider the buff
            # active. We want to change its end date to None.
            if today == end:
                buff['end'] = None
            
            buff_id = CorrelationBuff.save(buff)
            correlation['_id'] = buff_id
            correlation['state'] = buff['state']
            outstanding_buffs.append(buff)
    
    # Format the correlations as buffs.
    outstanding_buffs = list(CorrelationBuffCharts(current_user,
        outstanding_buffs, chart_prefix = "new_chart"))
    
    # Grab any buffs the user has previously accepted.
    accepted_buffs = {}
    max_end = None
    min_start = None
    
    for buff in CorrelationBuffCharts(current_user,
    CorrelationBuff.find_accepted(lazy = False), chart_prefix = "new_chart"):
        start_timestamp = int(time.mktime(
            datetime.datetime(*buff['start']).timetuple()))
        buff_key = ":".join(buff['paths']) + (
            "+" if buff["correlation"] > 0 else "-")
        
        if buff['end']:
            end_timestamp = int(
                time.mktime(datetime.datetime(*buff['end']).timetuple()))
        else:
            end_timestamp = time.localtime()
            active_buffs.append(buff)
            
        if max_end == None or end_timestamp > max_end:
            max_end = end_timestamp
            
        if min_start == None or start_timestamp < min_start:
            min_start = start_timestamp
        
        if buff_key not in accepted_buffs:
            accepted_buffs[buff_key] = {
                "icon": "/static/images/buffs/%s" % buff['icon'],
                "times": []}
            
        # Multiplying the times by 1000 because Javascript expects milliseconds.
        accepted_buffs[buff_key]["times"].append({
            "starting_time": start_timestamp * 1000,
            "ending_time": end_timestamp * 1000,
            "correlation": "%s%%" % int(round(buff["correlation"]*100)),
            "chart_data": buff["chart_data"],
            "chart_id": buff["chart_id"],
            "text": buff['text'],
            "title": buff['title']
        })
        
    bar_height = 40
    margin = {"left": 40, "right": 30, "top": 30, "bottom": 30}
    
    return render_template('%s/index.html' % app.name,
        active_buffs = active_buffs,
        outstanding_buffs = outstanding_buffs, 
        accepted_buffs = json.dumps(accepted_buffs.values()
            ) if accepted_buffs else None,
        OUTSTANDING = CorrelationBuff.OUTSTANDING,
        timeline_width = ((max_end - min_start)/10000
            ) if max_end and min_start else None,
        start_year = (datetime.datetime.fromtimestamp(min_start).year
            ) if min_start else None,
        bar_height = bar_height,
        margin = json.dumps(margin))

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
