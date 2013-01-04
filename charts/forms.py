from wtforms import Form, SelectField, validators
from auth import API

class ChartForm(Form):
    datastream = SelectField(u'Datastream')
    aspect = SelectField(u'Aspect', choices = list(
        (item, key) for key, item in API.get_aspects().items()))
    frequency = SelectField(u'Frequency', choices = list(
        (key, key) for key in API.get_frequencies()))
    chart_type = SelectField(u'Chart Type', choices = list(
        (key, key) for key in API.get_chart_types()))
    
    def __init__(self, user, *args, **kwargs):
        super(ChartForm, self).__init__(*args, **kwargs)
        self.datastream.choices = list(
            (key, key.title()) for key in user['uids'].keys())
