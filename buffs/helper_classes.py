import buffs.utils
import charts.utils
import itertools

class CorrelationBuffChart(object):
    colors = itertools.cycle(['steelblue', 'tomato'])
    chart_index = 0
        
    @classmethod
    def create(cls, user, buff, chart_id_prefix = "buff_chart_"):
            template = buffs.utils.get_template_for(buff)
            chart_data = charts.utils.json_for_buff(user, buff,
                colors = cls.colors)
            cls.chart_index += 1
            
            return {
                'title': template.title,
                'text': template.render_using(buff, chart_data),
                'chart_data': chart_data,
                'chart_id': chart_id_prefix + str(cls.chart_index),
                'buff_id': buff['_id'],
                'state': buff['state'],
                'start': buff['start'],
                'end': buff['end'],
                'correlation': buff['correlation'],
                'paths': buff['paths'],
                'icon': template.icon
            }
