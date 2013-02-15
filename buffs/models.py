from db.models import Model

class BuffTemplate(Model):
    table = "buff_template"
    
    def __init__(self, text, key = 'default', **kwargs):
        self.text = text
        self.key = key
        
    def render_using(self, correlation):
        return self.text.format(
            strength = int(correlation['correlation'] * 100),
            interval = correlation['interval'],
            start = correlation['start'][0:10],
            end = correlation['end'][0:10],
            aspects = ' and your '.join([(
                datastream.replace('_', ' ').title() + ' '
                + aspect.replace('_', ' ')+'s'
                 ) for datastream, aspect_list in correlation['aspects'].items(
                 ) for aspect in aspect_list])
        )

class CorrelationBuff(Model):
    table = "correlation_buffs"
    OUTSTANDING = 0
    ACCEPTED = 1
    DECLINED = 2
    
    def __init__(self, user_id = '', interval = '', start = '', end = '',
    correlation = 0, aspects = {}, state = OUTSTANDING):
        self.user_id = user_id
        self.interval = interval
        self.start = start
        self.end = end
        self.correlation = correlation
        self.aspects = aspects
        self.state = state
