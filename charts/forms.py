from wtforms import Form, SelectField, TextField, validators
from auth import API

class AdHocChartForm(Form):
    request_url = TextField(u'Request URL')

class ChartForm(Form):
    datastream = SelectField(u'Datastream')
    group_by = SelectField(u'Aggregation', choices = [
        ("year,month,day", 'day'),
        ("isoyear,isoweek", 'week'),
        ("year,month", 'month'),
        ("year", 'year')
    ])
    chart_type = SelectField(u'Chart Type', choices = [
        ('line', 'line'), ('bar', 'bar'), ('scatterplot', 'scatterplot'),
        ('area', 'area')])
    
    def __init__(self, datastreams, *args, **kwargs):
        super(ChartForm, self).__init__(*args, **kwargs)
        #self.datastream.value = (self.datastream.data if self.datastream.data != 'None'
        #                                   else datastreams[0])
                                           
        self.datastream.choices = [(stream[1]['href'], stream[1]['title']
            ) for stream in datastreams]
