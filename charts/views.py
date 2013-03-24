from decimal import Decimal
from flask import render_template, Blueprint, url_for, redirect, request
from flask.ext.login import current_user
from auth import API, BLUEPRINT
from charts.forms import ChartForm, AdHocChartForm
import json
import utils

app = Blueprint('charts', __name__, template_folder='/templates')

@app.route('/', methods = ['GET', 'POST'])
def index():
    
    datastreams = current_user['uids'].keys()
    #form = ChartForm(current_user, request.form)
    form = AdHocChartForm(request.form)
    form.chart_type = 'line'
    form.datastream = 'twitter'
    form.aspect = 'tweets'
    form.frequency = 'week'
    
    if request.method == 'POST' and form.validate():
        series = [{
        'name': "Adhoc data",#form.aspect.data.replace('_', ' '),
        'color': 'steelblue',
        'data': utils.format_chart_data(API.get(
                form.request_url.data, user = current_user
            ).content)
        }]
#        'data': utils.format_chart_data(API.get_chart_data(
#                current_user,form.datastream.data,
#                form.aspect.data, form.frequency.data
#            ), form.aspect.data)
    else:
        series = None
        
    return render_template('%s/index.html' % app.name,
            datastreams = datastreams,
            aspects = json.dumps(API.get_datastreams(current_user)),
            frequencies = API.get_intervals(),
            chart_types = API.get_chart_types(),
            form = form,
            series = series
    )
