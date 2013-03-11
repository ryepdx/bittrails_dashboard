from db.models import Model

class BuffTemplate(Model):
    table = "buff_template"
    
    def __init__(self, text, key = 'default', **kwargs):
        self.text = text
        self.key = key
        
    def render_using(self, correlation):
        return self.text.format(
            strength = int(correlation['correlation'] * 100),
            group_by = correlation['group_by'],
            start = correlation['start'][0:10],
            end = correlation['end'][0:10],
            paths = ' and your '.join([(path.replace('/', ' ').title()
                 ) for path in correlation['paths']])
        )

class CorrelationBuff(Model):
    table = "correlation_buffs"
    OUTSTANDING = 0
    ACCEPTED = 1
    DECLINED = 2
    
    def __init__(self, user_id = '', paths = [], group_by = [], start = '',
    end = '', correlation = 0, state = OUTSTANDING):
        self.user_id = user_id
        self.paths = paths
        self.group_by = group_by
        self.start = start
        self.end = end
        self.correlation = correlation
        self.state = state

    @classmethod
    def find_in_state(cls, state, lazy = True):
        results = cls.find({ 'state': state })
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
    def chart_id(self):
        return "chart" + self['_id'] 
