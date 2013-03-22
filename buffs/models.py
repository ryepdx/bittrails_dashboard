import pytz
from datetime import datetime
from db.models import Model

class BuffTemplate(Model):
    table = "buff_template"
    
    def __init__(self, text, key = 'default', title="Unkown Buff",
    icon="default.png", **kwargs):
        self.icon = icon
        self.title = title
        self.text = text
        self.key = key
        
    def render_using(self, correlation, charts):
        if len(correlation['group_by']) > 2:
            correlation['group_by'][-1] = "and " + correlation['group_by'][-1]
        return self.text.format(
            strength = int((correlation['correlation'] ** 2) * 100),
            inverse = "inverse " if correlation['correlation'] < 0 else "",
            group_by = ', '.join(correlation['group_by']),
            start = datetime(*correlation['start'][0:10]).strftime('%Y-%m-%d'),
            end = (datetime(*correlation['end'][0:10])
                if correlation['end'] else datetime.now(pytz.utc)
            ).strftime('%Y-%m-%d'),
            paths = ' and your '.join([chart['name'] for chart in charts])
        )

class CorrelationBuff(Model):
    table = "correlation_buffs"
    OUTSTANDING = 0
    ACCEPTED = 1
    DECLINED = 2
    
    def __init__(self, user_id = '', paths = [], group_by = [], start = '',
    end = '', correlation = 0, state = OUTSTANDING, **kwargs):
        self.user_id = user_id
        self.paths = paths
        self.group_by = group_by
        self.start = start
        self.end = end
        self.correlation = correlation
        self.state = state
        super(CorrelationBuff, self).__init__(**kwargs)

    @classmethod
    def find_in_state(cls, state, lazy = True, **kwargs):
        results = cls.find({ 'state': state }, **kwargs)
        if lazy:
            return results
        else:
            return [correlation for correlation in results]
        
    @classmethod
    def find_outstanding(cls, **kwargs):
        return cls.find_in_state(cls.OUTSTANDING, **kwargs)
        
    @classmethod
    def find_accepted(cls, **kwargs):
        return cls.find_in_state(cls.ACCEPTED, **kwargs)

    @property
    def key(self):
        return self.type_key + str(self.start)
        
    @property
    def type_key(self):
        return ":".join(self.paths) + ("+" if self.correlation > 0 else "-")

    @property
    def chart_id(self):
        return "chart" + self['_id'] 
