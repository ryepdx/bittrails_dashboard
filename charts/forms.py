from wtforms import Form, SelectField, TextField, validators
from auth import API

class AdHocChartForm(Form):
    request_url = TextField(u'Request URL')

class ChartForm(Form):
    datastream = SelectField(u'Datastream')
    aspect = SelectField(u'Aspect')
    frequency = SelectField(u'Frequency', choices = list(
        (key, key) for key in API.get_intervals()))
    chart_type = SelectField(u'Chart Type', choices = list(
        (key, key) for key in API.get_chart_types()))
    
    def __init__(self, user, *args, **kwargs):
        super(ChartForm, self).__init__(*args, **kwargs)
        datastreams = user['uids'].keys()
        datastream = (self.datastream.data if self.datastream.data != 'None'
                                           else datastreams[0])
        aspects = API.get_aspects()[datastream]['aspects']
        
        self.datastream.choices = list(
            (stream, stream.replace('_', ' ').title()) for stream in datastreams)
        self.aspect.choices = list(
            (aspect, aspect.replace('_', ' ')) for aspect in aspects)
