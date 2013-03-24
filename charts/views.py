import json
import utils

from decimal import Decimal
from flask import render_template, Blueprint, url_for, redirect, request
from flask.ext.login import current_user, login_required
from auth import API, BLUEPRINT
from charts import DEFAULT_DATASTREAMS
from charts.forms import ChartForm, AdHocChartForm

app = Blueprint('charts', __name__, template_folder='/templates')

@app.route('/', methods = ['GET', 'POST'])
@login_required
def index():
    custom_datastreams = [
        (stream, {'href': link['href'][0:-5] + '/totals',
                  'title': 'total ' + link['title']}
        ) for stream, link in API.get_custom_datastreams(current_user)]
        
    connected_datastreams = [(stream, link)
          for stream, link in DEFAULT_DATASTREAMS
          if stream in current_user.uids.keys()]
    form = ChartForm(custom_datastreams + connected_datastreams, request.form)
    chart_data = API.get_chart_data(
                current_user, form.datastream.data,
                form.group_by.data.split(',')
            )
    
    if request.method == 'POST' and form.validate():
        group_by_heading = dict(form.group_by.choices)[form.group_by.data]
        datastream_heading = dict(form.datastream.choices)[form.datastream.data]
        
        series = [{
        'name': datastream_heading,
        'color': 'steelblue',
        'data': utils.format_chart_data(chart_data['data'])
        }]
    else:
        series = None
        group_by_heading = None
        datastream_heading = None
        
    return render_template('%s/index.html' % app.name,
        form = form, series = series, group_by_heading = group_by_heading,
        datastream_heading = datastream_heading
    )
