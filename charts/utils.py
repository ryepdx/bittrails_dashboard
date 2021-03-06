import pytz
import datetime, time
from auth import API

# Found the following two functions at
# http://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar
def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta 


def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)


def json_for_buff(user, buff, colors):
    chart_series = []
    
    for path in buff['paths']:
        chart_data = API.get_chart_data(user, path, buff['group_by'],
            start = "%s-%s-%s" % tuple(buff['start']),
            end = buff['end'].strftime('%Y-%m-%d'
                ) if buff['end'] else datetime.datetime.now(pytz.utc
                ).strftime('%Y-%m-%d')
        )
        
        chart_series.append({
            'name': (chart_data['_links']['self']['title']
                ) if '_links' in chart_data and 'title' in chart_data['_links']['self'
                ] else path.replace('/', ' ').title(),
            'color': colors.next(),
            'data': format_chart_data(chart_data['data'])
        })
    return normalize_chart_series(chart_series)


def format_chart_data(data):
    # Right now it's a decent heuristic to assume that
    # the aspect ends with the dimension we want.
    # We are only concerned with 2D data for now.
    
    #dimension = path.split('_')[-1]
    formatted_data = []
    
    for datum in data:
        if "isoyear" in datum and "isoweek" in datum:
            datum_date = iso_to_gregorian(
                datum['isoyear'], datum['isoweek'], datum.get('isoweekday', 1))
        elif 'year' in datum and 'month' in datum and 'day' in datum:
            datum_date = datetime.datetime(
                datum.get('year'), datum.get('month', 1), datum.get('day', 1))
        else:
            datum_date = None
                
        if datum_date:
            formatted_data.append({
                'x': time.mktime(datum_date.timetuple()),
                'y': datum['value']
            })
        
    return sorted(formatted_data, key = lambda k: k['x'])

def normalize_chart_series(series):
    numerator = max(series[0]['data'], key = lambda x: x['y'])['y']
    
    for i in range(1, len(series)):
        multiplier = numerator / max(series[i]['data'],
            key = lambda x: x['y'])['y']
        series[i]['data'] = [{'x': row['x'], 'y': row['y'] * multiplier
            } for row in series[i]['data']]
            
    return series
