from flask import render_template, Blueprint, url_for, redirect, request
from flask.ext.login import current_user
from auth import API, BLUEPRINT
from charts.forms import ChartForm

app = Blueprint('charts', __name__, template_folder='/templates')

@app.route('/', methods = ['GET', 'POST'])
def index():
    
    datastreams = current_user['uids'].keys()
    #datastream = request.form.get('datastream')
    #chart = request.form.get('chart_type')
    #aspect = request.form.get('aspect')
    #frequency = request.form.get('frequency')
    
    form = ChartForm(current_user, request.form)
    
    if request.method == 'POST' and form.validate():
        data = API.get_chart_data(
            form.datastream.data, form.aspect.data, form.frequency.data
        )
    else:
        data = None
        
    return render_template('%s/index.html' % app.name,
            datastreams = datastreams,
            aspects = API.get_aspects(),
            frequencies = API.get_frequencies(),
            chart_types = API.get_chart_types(),
            data = data,
            form = form
    )