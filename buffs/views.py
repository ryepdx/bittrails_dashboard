import iso8601
import pymongo
import pytz
import itertools
import json
import bson
import datetime
import time
import charts.utils
import buffs.utils
import collections
from flask import render_template, Blueprint, url_for, redirect, request
from flask.ext.login import current_user, login_required
from auth import API, BLUEPRINT
from buffs.models import BuffTemplate, CorrelationBuff
from buffs.helper_classes import CorrelationBuffChart
from settings import SERVER_TIMEZONE

app = Blueprint('buffs', __name__, template_folder='/templates')

@app.route('/')
@login_required
def index():
    user_tz = current_user.get('timezone', pytz.utc)
    active_buffs = {}
    active_buff_charts = []
    accepted_buffs = {}
    outstanding_buffs = []
    all_paths = ['lastfm/scrobbles/echonest/totals',
             'lastfm/scrobbles/echonest/energy/averages']
             
    # Okay, time to add in custom paths!
    for datastream, href in API.get_custom_datastreams(current_user):
        if datastream != 'self':
            all_paths.append('custom/' + datastream + '/totals')
            all_paths.append('custom/' + datastream + '/averages')
        
    group_by_intervals = {
        "day": ["year","month","day"]#, "week": ["isoyear", "isoweek"],
        #"month": ["year", "month"], "year": ["year"]
    }
    continuous = True
    
    today = datetime.datetime.now(pytz.utc).replace(
        hour = 0, minute = 0, second = 0, microsecond = 0)
    
    # Keeping track of the max_end and min_start dates of the user's accepted
    # buffs so we can determine how wide the timeline needs to be in order to
    # get the amount of spacing between ticks we want.
    max_end = None
    min_start = None
    
    # Grab any buffs the user has previously accepted.
    for buff in CorrelationBuff.find_accepted(lazy = False):
        buff = CorrelationBuff(**buff)
        chart = CorrelationBuffChart.create(current_user, buff)
        start_timestamp = int(time.mktime(
            datetime.datetime(*buff.start, tzinfo = pytz.utc).timetuple()))
        
        # If the buff does not have a non-null end date, then we will just use
        # today. Null end dates indicate active buffs.
        if buff['end']:
            end_timestamp = int(time.mktime(
                pytz.UTC.localize(buff.end).timetuple()))
        else:
            end_timestamp = int(time.mktime(
                datetime.datetime.now(pytz.utc).timetuple()))
            active_buffs[buff.key] = buff
            active_buff_charts.append(chart)
            
        if max_end == None or end_timestamp > max_end:
            max_end = end_timestamp
            
        if min_start == None or start_timestamp < min_start:
            min_start = start_timestamp
        
        # Set up the JSON data the timeline expects.
        if buff.type_key not in accepted_buffs:
            accepted_buffs[buff.type_key] = {
                "icon": "/static/images/buffs/%s" % chart['icon'],
                "times": []}
            
        # Multiplying timestamps by 1000 because the timeline expects
        # milliseconds and Python uses seconds.
        accepted_buffs[buff.type_key]["times"].append({
            "starting_time": start_timestamp * 1000,
            "ending_time": end_timestamp * 1000,
            "correlation": "%s%%" % int(round(buff["correlation"]*100)),
            "chart_data": chart["chart_data"],
            "chart_id": chart["chart_id"],
            "text": chart['text'],
            "title": chart['title']
        })
        
    # Grab any correlations the user has yet to accept or decline.
    outstanding_buffs = CorrelationBuff.find_outstanding(lazy = False)
    
    # Grab the latest buff we logged, whether it was accepted or not.
    last_buff = CorrelationBuff.find_one(None, sort = [('$end', pymongo.DESCENDING)])
    a_year_ago = (today - datetime.timedelta(days = 365))

    if last_buff:
        last_buff['end'] = pytz.UTC.localize(last_buff['end'])
        start_date = max(a_year_ago,
            last_buff['end'] + datetime.timedelta(days = 1))
    else:
        start_date = a_year_ago
    
    # If there were active buffs, we want to ask for correlations from the start
    # date of the earliest one. That way we can see if the active buffs have
    # extended out any further. This may, of course, result in some completed
    # buffs being returned *again*, so we'll have to filter those out by making
    # sure we don't include any correlations with an end date before the end
    # date of last_buff.
    correlation_start_date = today
    if active_buffs:
        for buff in active_buffs.values():
            buff_start = datetime.datetime(*buff['start'], tzinfo = pytz.utc)
            
            if buff_start < correlation_start_date:
                correlation_start_date = buff_start
    else:
        correlation_start_date = start_date
    
    # Look for new correlations.
    for interval, group_by in group_by_intervals.items():
        intervalString = ",".join(sorted(group_by))
        
        # Look for new correlations in all combinations of paths.
        for paths in itertools.combinations(all_paths, 2):
            # Just grabbing the correlations for this user from the last 30 days
            # or since the last logged buff, whichever is later.
            new_correlations = API.get_correlations(current_user, paths, group_by,
                correlation_start_date, continuous = True)
            
            # Cache all the new correlations and update active buff end times
            # where applicable.
            for correlation in new_correlations:
                end = dict(zip(correlation['group_by'], correlation['end']))
                start = dict(zip(correlation['group_by'], correlation['start']))
                end = datetime.datetime(end['year'], end['month'], end['day'],
                    tzinfo = pytz.utc)
                start = datetime.datetime(start['year'], start['month'],
                    start['day'], tzinfo = pytz.utc)
                
                # If the correlation end date is today, then we consider the buff
                # active. We want to change its end date to None.
                if today == end:
                    correlation_end = None
                else:
                    correlation_end = end
                
                del correlation['end']
                buff = CorrelationBuff.find_or_create(
                    user_id = current_user['_id'], **correlation)
                    
                if 'end' in buff and buff['end']:
                    buff['end'] = pytz.UTC.localize(buff['end'])
                                    
                # If this has an start date greater than start_date, then we know
                # we need to save it. If not, and if it doesn't correspond to an
                # active buff, then we can ignore it. The user will have already
                # been prompted with it, by definition.
                # Also, don't append outstanding buffs with IDs, since they'll
                # already be a part of the outstanding_buffs list due to our
                # earlier Pymongo query.
                if (start > start_date 
                and buff['state'] == CorrelationBuff.OUTSTANDING
                and '_id' not in buff):
                    outstanding_buffs.append(buff)
                    
                # Update the buff end date, or save the new buff if it hasn't
                # been saved before.
                if (buff['end'] != correlation_end or '_id' not in buff):
                    buff['end'] = correlation_end
                    CorrelationBuff.save(buff)
                    
                # Does this "new correlation" correspond to a previously accepted
                # active buff? Does the new correlation provide an end date for that
                # active buff? Then update the buff's end date.
                if buff.key in active_buffs and end != today:
                    active_buffs[buff.key]['end'] = correlation_end
                    CorrelationBuff.save(buff)
    
    # Format the correlations as buffs.
    outstanding_buffs = [CorrelationBuffChart.create(current_user, buff
        ) for buff in outstanding_buffs]
        
    return render_template('%s/index.html' % app.name,
        active_buff_charts = active_buff_charts,
        outstanding_buffs = outstanding_buffs, 
        accepted_buffs = json.dumps(accepted_buffs.values()
            ) if accepted_buffs else None,
        OUTSTANDING = CorrelationBuff.OUTSTANDING,
        timeline_width = ((max_end - min_start)/10000
            ) if max_end and min_start else None,
        start_year = (datetime.datetime.fromtimestamp(min_start).year
            ) if min_start else None)

@app.route('/<buff_id>')
@login_required
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
